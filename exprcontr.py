
import numpy as np
from scipy.stats import poisson

def learning_contr(records):
    """Generate the contribution of doing each question to learning its corresponding concept.

    Args:
        records (np.ndarray): A numpy array of boolean values.
        True means the user has correctly answered the question; False otherwise.

    return:
        A list of contribution values each of which corresponds to the contribution of each question.
    """

    if len(records) == 0:
        return []

    contrs = np.zeros(len(records))

    for i, vc in enumerate(records):
        if i == 0:
            # First attempt
            if vc: contrs[i] = .5           # Previous=None & Current=Success => 0.50
            else: contrs[i] = .25           # Previous=None & Current=Failure => 0.25
        else:
            # Starting from the second attempt
            if vp:
                if vc: contrs[i] = 1.       # Previous=Success & Current=Success => 1.0
                else: contrs[i] = .25       # Previous=Success & Current=Failure => 0.25
            else:
                if vc: contrs[i] = .5       # Previous=Failure & Current=Success => 0.5
                else:
                    k = i - 2
                    if k < 0:
                        contrs[i] = 0.
                    else:
                        if contrs[k]:
                            contrs[i] = 0.
                        else:
                            contrs[i] = -.25
        vp = vc

    return contrs


def descending_weight(nfold):
    """Generate the weight of contribution for doing each question.

    Args:
        nfold (int): Number of attempts.

    returns:
        A list of weights each of which corresponds to the weight of contribution for a specific attempt.
        Later attempts are given more weights.
    """

    if not isinstance(nfold, int) or nfold <= 0:
        raise ValueError("nfold must be a positive integer.")

    denom = nfold * (nfold + 1) / 2

    return np.array([(i + 1) / denom for i in range(nfold)])


def expr_pcontr(records):
    """Calculate the probability of a user correctly answering the next question from a specific concept
    given the his/her records of doing other questions from the same concept.

    Args:
        records (np.ndarray): A numpy array of boolean values.
        True means the user has correctly answered the question; False otherwise.

    returns:
        The probability of a user correctly answering the next question only considering his/her records
        and nothing else. Note that this probability is an extra probability that will be added to other
        probabilities to make up the true probability of the user correctly solving the next question.
    """

    if len(records) == 0:
        return 0

    contrs = learning_contr(records)
    weights = descending_weight(len(records))
    tot = np.dot(contrs, weights)

    # If we would produce probabily and generate fake records based only on the previous records,
    # in the case when the user fails to answer the first few question, the probability would become
    # extremely low and lower after. Hence, we need to add an extra part to it. We can assume that
    # the more questions the user has done in this concept, the more likely s/he would answer the
    # question correctly. Here, to achieve this effect, we introduce the CDF of poisson distribution.

    lam = 5

    return  1/3 * tot + 2/3 * poisson.cdf(len(records), lam) 


def main():
    import matplotlib.pyplot as plt
    import random

    nqs, nc = (10, 50, 100, 1000), 5
    figure, axes = plt.subplots(nrows=len(nqs), ncols=nc)

    cols = [f'sim #{c+1}' for c in range(nc)]
    rows = [f'{nq} trials' for nq in nqs]

    for ax, col in zip(axes[0], cols):
        ax.set_title(col)

    for ax, row in zip(axes[:,0], rows):
        ax.set_ylabel(row, rotation=90, size='large')

    for r, nq in enumerate(nqs):
        for c in range(nc):
            count = 0
            user_records = np.empty(nq, dtype=bool)
            user_probs = np.empty(nq)
            accuracy = np.empty(nq)

            for i in range(nq):
                p = .25 + .65 * expr_pcontr(user_records[:nq+1]) + .1 * random.randint(0, 1)
                a = random.choices([True, False], weights=[p, 1-p], k=1)[0]
                if a: count += 1

                user_probs[i] = p
                user_records[i] = a
                accuracy[i] = count / (i + 1)

            axes[r, c].plot([i+1 for i in range(nq)], accuracy)
            axes[r, c].set_ylim(0, 1.2)

    plt.xlabel("number of trials")
    plt.ylabel("accuracy")
    figure.suptitle("Accuracy Simulation for Different Trial Numbers")

    plt.show()


if __name__ == '__main__':

    main()