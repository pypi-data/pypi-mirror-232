import nltk
import string
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, confusion_matrix, \
    precision_recall_fscore_support
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# nltk.download('stopwords')

# Load the stopwords and create a set for faster lookup
stop_words = set(nltk.corpus.stopwords.words('english'))


class TextMatcher:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()

    def preprocess_and_tokenize(self, text):
        # Remove punctuation and convert to lowercase
        text = ''.join([char for char in text if char not in string.punctuation])
        text = text.lower()

        # Tokenize the text and remove stopwords
        words = nltk.word_tokenize(text)
        words = [word for word in words if word not in stop_words]

        return words

    def match_texts(self, truth_list, pred_list, match_type='direct_match', cosine_threshold=0.8):
        if match_type == 'direct_match':
            labels = self.direct_match(truth_list, pred_list)
        elif match_type == 'token_overlap':
            labels = self.token_overlap_match(truth_list, pred_list)
        elif match_type == 'cosine_similarity':
            labels = self.cosine_similarity_match(truth_list, pred_list, cosine_threshold)
        else:
            raise ValueError("Invalid match_type. Use 'direct_match', 'token_overlap', or 'cosine_similarity'.")

        metrics = self.calculate_metrics(labels)
        return metrics

    def direct_match(self, truth_list, pred_list):
        # Initialize a list to store binary labels
        labels = []

        # Iterate through each item in pred_list
        for pred_text, truth_text in zip(pred_list, truth_list):
            match_found = False

            # Preprocess and tokenize the predicted text
            pred_tokens = set(self.preprocess_and_tokenize(pred_text))

            # Preprocess and tokenize the truth text
            truth_tokens = set(self.preprocess_and_tokenize(truth_text))

            # Check if there is an exact match between predicted and truth tokens
            if pred_tokens == truth_tokens:
                labels.append(1)  # Match found
                match_found = True

            # If no match is found for the current pred_text
            if not match_found:
                labels.append(0)  # No match found

        return labels

    def token_overlap_match(self, truth_list, pred_list):
        # Initialize a list to store binary labels
        labels = []

        # Iterate through each item in pred_list
        for pred_text, truth_text in zip(pred_list, truth_list):
            match_found = False

            # Preprocess and tokenize the predicted text
            pred_tokens = set(self.preprocess_and_tokenize(pred_text))

            # Preprocess and tokenize the truth text
            truth_tokens = set(self.preprocess_and_tokenize(truth_text))

            # Check if there is any token overlap between predicted and truth tokens
            if pred_tokens.intersection(truth_tokens):
                labels.append(1)  # Match found
                match_found = True

            # If no match is found for the current pred_text
            if not match_found:
                labels.append(0)  # No match found

        return labels

    def cosine_similarity_match(self, truth_list, pred_list, cosine_threshold=0.8):
        truth_processed = [' '.join(self.preprocess_and_tokenize(text)) for text in truth_list]
        pred_processed = [' '.join(self.preprocess_and_tokenize(text)) for text in pred_list]

        # Create TF-IDF vectors for the processed text data
        truth_tfidf = self.vectorizer.fit_transform(truth_processed)
        pred_tfidf = self.vectorizer.transform(pred_processed)

        # Initialize a list to store the binary labels (1 for matches, 0 for non-matches)
        labels_co = []

        # Iterate through each pair of tokenized lists
        for pred, truth in zip(pred_processed, truth_processed):
            # Create TF-IDF vectors for the current pair
            pred_tfidf_single = self.vectorizer.transform([pred])
            truth_tfidf_single = self.vectorizer.transform([truth])

            # Calculate cosine similarity between the TF-IDF vectors for the current pair
            cosine_sim_single = cosine_similarity(pred_tfidf_single, truth_tfidf_single)[0][0]

            # Append 1 if cosine similarity is greater than or equal to the threshold, otherwise append 0
            if cosine_sim_single >= cosine_threshold:
                labels_co.append(1)
            else:
                labels_co.append(0)
        return labels_co

    def calculate_metrics(self, labels):
        true_labels = [1] * len(labels)  # Ground truth labels for the positive class
        if all(label == 0 for label in labels):  # All labels are 0
            precision = recall = f1 = 0  # Set precision, recall, and F1 to 0
            fn = len(labels)  # Set TN to the total number of labels
            fp = tp = tn = 0  # Set other metrics to 0
            specificity = npv = fpr = fnr = fdr = accuracy = tpr = ppv = tnr = 0  # Set other metrics to 0
        elif all(label == 1 for label in labels):  # All labels are 1
            precision = recall = f1 = 1  # Set precision, recall, and F1 to 1
            tp = len(labels)  # Set TP to the total number of labels
            tn = fp = fn = 0  # Set other metrics to 0
            specificity = npv = fpr = fnr = fdr = accuracy = tpr = ppv = tnr = 1  # Set other metrics to 1
        else:
        # Calculate precision, recall, and f1_score
            precision = precision_score(true_labels, labels)
            recall = recall_score(true_labels, labels)
            f1 = f1_score(true_labels, labels)

            # Calculate confusion matrix to compute other metrics
            tn, fp, fn, tp = confusion_matrix(true_labels, labels).ravel()

            # Calculate specificity (TNR)
            specificity = tn / (tn + fp)

            # Calculate negative predictive value (NPV)
            npv = tn / (tn + fn)

            # Calculate false positive rate (FPR)
            fpr = fp / (fp + tn)

            # Calculate false negative rate (FNR)
            fnr = fn / (fn + tp)

            # Calculate false discovery rate (FDR)
            fdr = fp / (fp + tp)

            # Calculate accuracy
            accuracy = accuracy_score(true_labels, labels)

            # Calculate true positive rate (TPR)
            tpr = tp / (tp + fn)

            # Calculate positive predictive value (PPV)
            ppv = tp / (tp + fp)

            # Calculate true negative rate (TNR)
            tnr = tn / (tn + fp)
            macro_precision, macro_recall, macro_f1, _ = precision_recall_fscore_support(true_labels, labels,
                                                                                         average='macro')
            weighted_precision, weighted_recall, weighted_f1, _ = precision_recall_fscore_support(true_labels, labels,
                                                                                                  average='weighted')

            return {
                "Precision": precision,
                "Recall": recall,
                "Specificity": specificity,
                "F1 Score": f1,
                "Negative Predictive Value (NPV)": npv,
                "False Positive Rate (FPR)": fpr,
                "False Negative Rate (FNR)": fnr,
                "False Discovery Rate (FDR)": fdr,
                "Accuracy": accuracy,
                "True Positive Rate (TPR)": tpr,
                "Positive Predictive Value (PPV)": ppv,
                "True Negative Rate (TNR)": tnr,
                "Macro Average Precision": macro_precision,
                "Macro Average Recall": macro_recall,
                "Macro Average F1 Score": macro_f1,
                "Weighted Average Precision": weighted_precision,
                "Weighted Average Recall": weighted_recall,
                "Weighted Average F1 Score": weighted_f1,
            }

text_matcher = TextMatcher()