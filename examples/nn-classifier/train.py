import argparse
import easyopt
import numpy as np

from sklearn.neural_network import MLPClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

parser = argparse.ArgumentParser()

parser.add_argument("--hidden-layer-l1", type=int, default=100)
parser.add_argument("--hidden-layer-l2", type=int, default=100)
parser.add_argument("--lr", type=float, default=1e-3)
parser.add_argument("--epochs", type=int, default=100)

args = parser.parse_args()

X, y = make_classification(n_samples=200, random_state=1)
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, random_state=1)
X_test, X_val, y_test, y_val = train_test_split(X_train, y_train, random_state=1, train_size=0.5)


clf = MLPClassifier(
    hidden_layer_sizes=(args.hidden_layer_l1, args.hidden_layer_l2),
    learning_rate_init=args.lr
)

for epoch in range(0, args.epochs):
    clf.partial_fit(X_train, y_train, np.unique(y))
    if epoch % 5 == 0:
        val_score = clf.score(X_val, y_val)
        easyopt.report(val_score)
        if easyopt.should_prune():
            break

val_score = clf.score(X_val, y_val)
easyopt.objective(val_score)

test_score = clf.score(X_test, y_test)
print(f"test score: {test_score}")
