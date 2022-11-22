import logging

import numpy as np
from scipy import linalg
from scipy.special import expit, logit

from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.preprocessing import LabelBinarizer, Normalizer
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
from sklearn.utils.multiclass import unique_labels
from sklearn.metrics import accuracy_score, mean_squared_error, f1_score

from timeit import default_timer

import matplotlib.pyplot as plt

log = logging.getLogger(__name__)


def soft_thresholding(a, b):
    return np.sign(a) * np.maximum(np.abs(a) - b, 0)


def linear(x):
    return x


def sigmoid(x):
    return np.where(x >= 0,
                    1 / (1 + np.exp(-x)),
                    np.exp(x) / (1 + np.exp(x)))


def inverse_sigmoid(x, eps=1e-6):
    z = np.clip(x, eps, 1 - eps)
    return logit(z)


def soft_plus(x, beta=1, threshold=20):
    return np.where(x * beta > threshold,
                    x,
                    (1 / beta) * np.log(1 + np.exp(beta * x)))


def soft_plus_inverse(x):
    log.debug(f"SoftPlus Inverse x >? 0: {(x > 0).all()}")
    x = np.clip(x, 1e-6, None)
    assert (x > 0).all(), "Some values are equal or less than zero"
    threshold = np.log(np.finfo(x.dtype).eps) + 2
    is_too_small = x < np.exp(threshold)
    is_too_large = x > -threshold
    too_small_value = np.log(x)
    too_large_value = x
    x = np.where(is_too_small | is_too_large, np.ones([], x.dtype), x)
    y = x + np.log(-np.expm1(-x))
    return np.where(is_too_small,
                    too_small_value,
                    np.where(is_too_large, too_large_value, y))


class MPDLLRClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, lmd=1, beta=1, alpha_1=1, alpha_2=1, alpha_3=1, tau=1, a_1=10, a_2=50,
                 transfer_function='soft_plus', X_c=None, normalize=True, max_iter=100, patience=np.inf):

        self.lmd = lmd
        self.beta = beta
        self.alpha_1 = alpha_1
        self.alpha_2 = alpha_2
        self.alpha_3 = alpha_3
        self.tau = tau
        self.a_1 = a_1
        self.a_2 = a_2
        self.X_c = X_c
        assert transfer_function in ['linear', 'sigmoid',
                                     'soft_plus'], f"{transfer_function} is an invalid valid option"
        self.transfer_function = transfer_function
        self.normalize = normalize
        self.max_iter = max_iter
        self.patience = patience

    def fit(self, X, y):
        # Check that X and y have correct shape
        X, y = check_X_y(X, y)
        self.__set_transfer_function()

        if isinstance(self.X_c, np.ndarray):
            X_c = self.X_c[:X.shape[0]]
        elif self.X_c == 'svd':
            X_mean = np.mean(X, axis=0)
            X_hat = X - X_mean
            U, _, Vh = linalg.svd(X_hat.swapaxes(0, 1),
                                  full_matrices=True,
                                  lapack_driver='gesvd')
            X_c = U[:, :3] @ Vh[:3, :]
            X_c = np.swapaxes(X_c, 0, 1)
            # plt.pcolor(X_c, cmap='gist_gray')
            # plt.gca().invert_yaxis()
        elif self.X_c == 'avg':
            X_c = X - np.mean(X, axis=0, keepdims=True) - X
        elif self.X_c == 'split':
            #print(f"X shape: {X.shape}")
            qt = X.shape[1]//2
            X, X_c = X[:, :qt], X[:, qt:]
            #print(f"1 X shape: {X.shape}")
            #print(f"2 X_c shape: {X_c.shape}")

        # self.transformer = Normalizer('max').fit(X_c)
        # X = self.transformer.transform(X)
        # X_c = self.transformer.transform(X_c)

        X = np.swapaxes(X, 0, 1)
        X = X / np.amax(np.abs(X), axis=0, keepdims=True)
        X_c = np.swapaxes(X_c, 0, 1)
        X_c = X_c / np.amax(np.abs(X_c), axis=0, keepdims=True)

        #print(f"X shape: {X.shape}")
        #print(f"X_c shape: {X_c.shape}")
        assert X_c.shape == X.shape, f"X shape {X.shape} is different from X_c shape {X_c.shape}"
        n_timesteps = X.shape[0]
        self.n_timesteps_ = n_timesteps

        # Store the classes seen during fit
        self.classes_ = unique_labels(y)
        n_classes = self.classes_.size
        self.n_classes = n_classes

        n_samples = y.size

        self.b_1 = self.a_1 // self.n_classes
        self.a_1 = self.n_classes * self.b_1

        lb = LabelBinarizer()
        H = lb.fit_transform(y)
        log.debug(f"H before if: {H[0]}")
        if H.shape[1] < 2:
            log.debug(f"Entered in H if")
            H = np.insert(H, 0, 1 - H.flatten(), axis=1)
        log.debug(f"H after if: {H[0]}")
        H = np.swapaxes(H, 0, 1)
        log.debug(f"H after swap: {H[:, 0]}")
        log.debug(f"H calculated from y with shape: {H.shape}")

        W = np.random.uniform(0, 1, (n_classes, self.a_1))
        log.debug(f"W initialized with shape: {W.shape}")

        B = -1 * np.ones((n_classes, n_samples))
        B[H == 1] = 1
        log.debug(f"B initialized with shape: {B.shape}")

        A_1 = np.random.uniform(0, 1, (self.a_1, self.a_2))
        log.debug(f"A_1 initialized with shape: {A_1.shape}")

        A_2 = np.random.uniform(0, 1, (self.a_2, n_timesteps))
        log.debug(f"A_2 initialized with shape: {A_2.shape}")

        start = default_timer()
        U, s, Vh = linalg.svd(X_c,
                              full_matrices=False,
                              lapack_driver='gesvd')
        end = default_timer()
        log.debug(f"SDV for P took: {end - start} s")
        u = U[:, 0]
        vh = Vh[0, :self.n_timesteps_]
        P = u @ u.T
        log.debug(f"P initialized with shape: {P.shape}")

        Z = np.zeros((self.a_2, n_samples))
        D_list = [np.random.uniform(0, 1, (n_timesteps, self.b_1)) for _ in range(n_classes)]
        log.debug("D list initialized")
        S_list = [np.random.uniform(0, 1, (self.b_1, X[:, y == i].shape[1])) for i in range(n_classes)]
        log.debug("S list initialized")
        # Samples are assumed to be sorted by class for now
        Phi_list = [np.eye(self.a_1, self.b_1, -i * self.b_1) for i in range(n_classes)]
        log.debug("Phi list initialized")
        Y = np.column_stack([D_i @ S_i for D_i, S_i in zip(D_list, S_list)])
        log.debug(f"Y calculated from D and S  with shape: {Y.shape}")
        Y_hat = np.column_stack([Phi_i @ S_i for Phi_i, S_i in zip(Phi_list, S_list)])
        log.debug(f"Y hat calculated from Phi and  with shape: {Y_hat.shape}")
        M = np.zeros((n_classes, n_samples))
        log.debug(f"M initialized with shape: {M.shape}")
        C_list = [np.zeros((n_timesteps, self.b_1)) for _ in range(n_classes)]
        log.debug(f"C list initialized")
        G = np.zeros((n_timesteps, n_samples))
        log.debug(f"G initialized with shape: {G.shape}")
        N = np.zeros((self.a_2, n_samples))
        log.debug(f"N initialized with shape: {N.shape}")
        R = np.zeros((n_timesteps, n_timesteps))
        log.debug(f"R initialized with shape: {R.shape}")
        Q_list = [np.zeros((n_timesteps, self.b_1)) for _ in range(n_classes)]
        log.debug(f"Q list initialized")
        E = np.zeros((n_timesteps, n_samples))
        log.debug(f"E initialized with shape: {E.shape}")
        Z = self.transfer_function(A_2 @ (np.identity(n_timesteps) - P) @ X)
        log.debug(f"Z initialized with shape: {Z.shape}")

        mu, mu_max, rho = 1e-3, 1e5, 1.20
        zeta = 0.001
        k = 0

        log.debug("Z to abs value")
        # self.lmd = 0.50*np.linalg.norm(X_c, np.inf)
        history = []
        mse = np.inf
        score = 0
        patience = 0
        while k < self.max_iter and mse > zeta:
            log.debug(f"Iteration: {k} ")
            U, s, Vh = linalg.svd(P + R / mu,
                                  full_matrices=False,
                                  lapack_driver='gesvd')
            Sigma = np.diag(s)
            J = U @ soft_thresholding(Sigma, self.lmd / mu) @ Vh
            A_syl = np.identity(n_timesteps) + mu * A_2.T @ A_2
            X_X_T = linalg.inv(X @ X.T)
            B_syl = (mu * np.identity(n_timesteps) + mu * X_c @ X_c.T) @ X_X_T
            Q_syl = ((X - Y) @ X.T + mu * (J - R / mu) + mu * (X_c - E + G / mu) @ X_c.T + mu * A_2.T @ (
                    A_2 @ X - self.inverse_transfer_function(Z + N / mu)) @ X.T) @ X_X_T
            P = linalg.solve_sylvester(A_syl, B_syl, Q_syl)
            E_hat = X_c - P @ X_c + G / mu
            for j in range(E.shape[1]):
                E[:, j] = E_hat[:, j] / linalg.norm(E_hat[:, j], 2) * np.maximum(
                    linalg.norm(E_hat[:, j], 2) - self.beta / mu, 0)

            for i in range(n_classes):
                X_i, Z_i = X[:, y == i], Z[:, y == i]
                D_i, C_i, S_i, Phi_i = D_list[i], C_list[i], S_list[i], Phi_list[i]
                S_i_neg = np.column_stack([S_i for j in range(n_classes) if j != i])
                U, s, Vh = linalg.svd(D_i + C_i / mu,
                                      full_matrices=False,
                                      lapack_driver='gesvd')
                Sigma = np.diag(s)
                Q_i = U @ soft_thresholding(Sigma, self.alpha_1 / mu) @ Vh
                Omega = (np.identity(n_timesteps) - P) @ X_i @ S_i.T + mu * (Q_i - C_i / mu)
                D_i = Omega @ linalg.inv(
                    S_i @ S_i.T + 2 * self.alpha_2 * S_i_neg @ S_i_neg.T + mu * np.identity(self.b_1))
                for j in range(D_i.shape[1]):
                    D_i[:, j] = D_i[:, j] / np.maximum(linalg.norm(D_i[:, j]), 1)
                Omega_hat = linalg.inv(D_i.T @ D_i + 2 * self.alpha_3 * S_i_neg @ S_i_neg.T + Phi_i.T @ Phi_i)
                S_i = Omega_hat @ (D_i.T @ (np.identity(n_timesteps) - P) @ X_i + Phi_i.T @ A_1 @ Z_i)

                Q_list[i], D_list[i], S_list[i] = Q_i, D_i, S_i

            Y = np.column_stack([D_i @ S_i for D_i, S_i in zip(D_list, S_list)])
            Y_hat = np.column_stack([Phi_i @ S_i for Phi_i, S_i in zip(Phi_list, S_list)])

            Theta = mu * (self.transfer_function(A_2 @ (np.identity(n_timesteps) - P) @ X) - N / mu)
            Upsilon = A_1.T @ Y_hat + Theta + (W @ A_1).T @ (H + B * M)
            Z = linalg.inv(A_1.T @ A_1 + mu * np.identity(self.a_2) + (W @ A_1).T @ (W @ A_1)) @ Upsilon
            # Z = np.clip(Z, 1e-6, None)

            F = W.T @ (H + B * M) + Y_hat
            U, _, Vh = linalg.svd((linalg.inv(np.identity(self.a_1) - W.T @ W) @ F) @ Z.T,
                                  full_matrices=False,
                                  lapack_driver='gesvd')
            A_1 = U @ Vh

            # A_1 = linalg.orthogonal_procrustes(Z.T, (linalg.inv(np.identity(self.a_1) + W.T @ W) @ F) @ Z.T, check_finite=True)

            U, _, Vh = linalg.svd(self.inverse_transfer_function(Z + N / mu) @ ((np.identity(n_timesteps) - P) @ X).T,
                                  full_matrices=False,
                                  lapack_driver='gesvd')
            A_2 = U @ Vh

            F_hat = linalg.inv((A_1 @ Z) @ (A_1 @ Z).T + self.tau * np.identity(self.a_1))
            W = ((H + B * M) @ (A_1 @ Z).T) @ F_hat

            M_hat = W @ A_1 @ Z - H
            M = np.maximum(B * M_hat, 0)

            for i in range(n_classes):
                C_i, D_i, Q_i = C_list[i], D_list[i], Q_list[i]
                C_i = C_i + mu * (D_i - Q_i)
                C_list[i] = C_i

            G = G + mu * (X_c - (P @ X_c + E))
            N = N + mu * (Z - self.transfer_function(A_2 @ (np.identity(n_timesteps) - P) @ X))
            R = R + mu * (P - J)

            #of = self.objective_function(X, X_c, y, H, W, A_1, A_2, P, Z, J, B, D_list, S_list, M, C_list, G, N, R,
            #                             Q_list, E, Phi_list, mu)
            of = self.__objective_function(P,E,X,y,H,B,M,W,A_1,A_2,D_list,S_list,Phi_list)
            log.debug(f"Objetive function value at iteration {k}: {of:.2f}")

            y_pred = self.__predict_function(X, W, A_1, A_2, P)
            mse = mean_squared_error(y, y_pred)
            acc = accuracy_score(y, y_pred)
            f1 = f1_score(y, y_pred, average="macro")
            if f1 > score:
                score = f1
                patience = 0
                self.W_ = W
                self.A_1_ = A_1
                self.A_2_ = A_2
                self.P_ = P
            else:
                patience+=1
            log.debug(f"Accuracy of {k} iteration: {acc:.2f}")
            log.debug(f"F1-Score of {k} iteration: {f1:.2f}")

            history.append(of)

            mu = np.minimum(rho * mu, mu_max)
            k += 1
            if patience > self.patience:
                break

        log.debug(f"Check constraints:")
        log.debug(
            f"||d_ij||_2 <=? 1: {np.array([linalg.norm(D_i[:, j], 2) <= 1 for D_i in D_list for j in range(D_i.shape[1])]).all()}")
        log.debug(f"M >=? 0: {(M >= 0).all()}")
        log.debug(f"A_1@A_1.T =? I: {np.isclose(A_1 @ A_1.T, np.identity(self.a_1)).all()}")
        log.debug(f"A_2@A_2.T =? I: {np.isclose(A_2 @ A_2.T, np.identity(self.a_2)).all()}")
        log.debug("Others checks")
        log.debug(f" X_c =? P@X_c + E: {np.isclose(X_c, P @ X_c + E).all()}")

        #self.W_ = W
        #self.A_1_ = A_1
        #self.A_2_ = A_2
        #self.P_ = P

        plt.plot(history)

        return self

    def __preprocess(self, X):
        check_is_fitted(self)
        if self.X_c == "split" and X.shape[1] != self.n_timesteps_:
            q_t = X.shape[1] // 2
            X = X[:, :q_t]
        if self.normalize:
            X = X / np.amax(np.abs(X), axis=1, keepdims=True)
        X = np.swapaxes(X, 0, 1)
        return X

    def decision_function(self, X):
        X = self.__preprocess(X)
        H = self.W_ @ self.A_1_ @ self.transfer_function(self.A_2_ @ (np.identity(self.n_timesteps_) - self.P_) @ X)
        return H.swapaxes(0, 1)

    def __predict_function(self, X, W, A_1, A_2, P):
        H = W @ A_1 @ self.transfer_function(A_2 @ (np.identity(self.n_timesteps_) - P) @ X)
        y = np.argmax(H, axis=0)
        return y

    def predict(self, X):
        # Check if fit has been called
        X = self.__preprocess(X)
        y = self.__predict_function(X, self.W_, self.A_1_, self.A_2_, self.P_)

        return y

    def remove_clutter(self, X):
        X = self.__preprocess(X)
        X_t = (np.identity(self.n_timesteps_) - self.P_) @ X

        return X_t.swapaxes(0, 1)

    def get_coding(self, X):
        X = self.__preprocess(X)
        S = self.A_1_ @ self.transfer_function(self.A_2_ @ (np.identity(self.n_timesteps_) - self.P_) @ X)
        return S.swapaxes(0, 1)

    def objective_function(self, X, X_c, y, H, W, A_1, A_2, P, Z, J, B, D_list, S_list, M, C_list, G, N, R, Q_list, E,
                           Phi_list, mu):
        n_classes = self.n_classes
        n_timesteps = self.n_timesteps_
        of_1 = 0
        for i in range(n_classes):
            X_i, Z_i = X[:, y == i], Z[:, y == i]
            D_i, C_i, S_i, Phi_i, Q_i = D_list[i], C_list[i], S_list[i], Phi_list[i], Q_list[i]
            S_i_neg = np.column_stack([S_i for j in range(n_classes) if i != j])
            of_1 += 0.5 * linalg.norm((np.identity(n_timesteps) - P) @ X_i - D_i @ S_i) ** 2
            + self.alpha_1 * linalg.norm(Q_i)
            + self.alpha_2 * linalg.norm(D_i @ S_i_neg) ** 2
            + self.alpha_3 * linalg.norm(S_i_neg.T @ S_i_neg) ** 2
            + 0.5 * linalg.norm(A_1 @ Z_i - Phi_i @ S_i) ** 2

        of_2 = self.lmd * linalg.norm(J, 'nuc')
        of_3 = np.sum(linalg.norm(E, ord=2, axis=1))
        of_4 = 0.5 * linalg.norm((H + B * M) - W @ A_1 @ Z) ** 2
        of_5 = self.tau * linalg.norm(W) ** 2
        of_6 = 0.5 * mu * linalg.norm(X_c - (P @ X_c + E) + G / mu) ** 2
        of_7 = 0.5 * mu * linalg.norm(P - J + R / mu) ** 2
        of_8 = 0.5 * mu * linalg.norm(
            Z - self.transfer_function(A_2 @ (np.identity(n_timesteps) - P) @ X) + N / mu) ** 2
        of_9 = 0
        for i in range(n_classes):
            D_i, Q_i, C_i = D_list[i], Q_list[i], C_list[i]
            of_9 += linalg.norm(D_i - Q_i + C_i / mu) ** 2
        of_9 = 0.5 * mu * of_9
        of = of_1 + of_2 + of_3 + of_4 + of_5 + of_6 + of_7 + of_8 + of_9
        # of = of_8
        return of

    def __objective_function(self, P, E, X, y, H, B, M, W, A_1, A_2, D_list, S_list, Phi_list):
        n_classes = self.n_classes
        n_timesteps = self.n_timesteps_
        X_t = (np.identity(n_timesteps) - P) @ X

        of_1 = self.lmd * linalg.norm(P, 'nuc')
        of_2 = self.beta * np.sum(linalg.norm(E, ord=2, axis=1))
        of_3 = 0
        for i in range(n_classes):
            X_i_t = X_t[:, y == i]
            D_i, S_i, Phi_i= D_list[i], S_list[i], Phi_list[i]
            S_i_neg = np.column_stack([S_i for j in range(n_classes) if i != j])
            of_3+= 0.5*linalg.norm(X_i_t - D_i@S_i)**2
            + self.alpha_1*linalg.norm(D_i, 'nuc')
            + self.alpha_2*linalg.norm(D_i@S_i_neg)**2
            + self.alpha_3*linalg.norm(S_i_neg.T@S_i)**2
            + 0.5*linalg.norm(A_1@self.transfer_function(A_2@X_i_t)-Phi_i@S_i)**2
        of_4 = 0.5*linalg.norm((H+B*M)-W@A_1@self.transfer_function(A_2@X_t))**2
        of_5 = self.tau*linalg.norm(W)**2
        of = of_1+of_2+of_3+of_4+of_5
        return of

    def __set_transfer_function(self):
        if self.transfer_function == 'soft_plus':
            self.transfer_function = soft_plus
            self.inverse_transfer_function = soft_plus_inverse
        elif self.transfer_function == 'linear':
            self.transfer_function = linear
            self.inverse_transfer_function = linear
        elif self.transfer_function == 'sigmoid':
            self.transfer_function = sigmoid
            self.inverse_transfer_function = inverse_sigmoid
        else:
            self.transfer_function = linear
            self.inverse_transfer_function = linear
