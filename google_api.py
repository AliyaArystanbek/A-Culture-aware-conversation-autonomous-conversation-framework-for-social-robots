# Imports the Google Cloud client library
from google.cloud import language_v1


# Instantiates a client
client = language_v1.LanguageServiceClient()

# The text to analyze
text = u"I want to eat pakora and samosa. I want to eat pakora and samosa.I want to eat pakora and samosa.I want to eat pakora and samosa."
document = language_v1.Document(
    content=text, type_=language_v1.Document.Type.PLAIN_TEXT
)

# Detects the sentiment of the text
sentiment = client.analyze_sentiment(
    request={"document": document}
).document_sentiment

print("Text: {}".format(text))
print("Sentiment: {}, {}".format(sentiment.score, sentiment.magnitude))

categories = client.classify_text(
	request={"document": document}
).categories
for category in categories:
	print(u"=" * 20)
	print(u"{:<16}: {}".format("category", category.name))
	print(u"{:<16}: {}".format("confidence", category.confidence))
