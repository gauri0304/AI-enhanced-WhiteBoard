import sqlite3
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import nltk

nltk.download('punkt')

def fetch_and_summarize(topic):
    # Connect to SQLite database
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    # Query to retrieve relevant information based on user input
    cursor.execute('''
           SELECT topic, info
           FROM my_table
           WHERE subject IN ('Physics', 'Chemistry', 'Biology', 'Mathematics')
               AND LOWER(topic) = LOWER(?)
       ''', (topic,))

    # Fetch all results
    results = cursor.fetchall()
    conn.close()

    #If no relevant information found, return None
    #if not results:
        #return ("No relevant information found")

    # Combine all contents from the query result
    combined_content = ' '.join([result[1] for result in results])

    # Summarize using sumy LexRank summarizer
    parser = PlaintextParser.from_string(combined_content, Tokenizer("english"))
    stemmer = Stemmer("english")
    summarizer = LexRankSummarizer(stemmer)
    summarizer.stop_words = get_stop_words("english")

    # Increase the number of sentences to include in the summary to cover more content
    summary_sentences = summarizer(parser.document, 10)  # Get top 10 sentences
    summary = ' '"\n".join(str(sentence) for sentence in summary_sentences)

    return summary
    # Return topic of the first result and the summary


    '''return{
        "topic": results[0][0],
        "summary": summary
    }'''


'''if __name__ == "__main__":

    while True:
        topic = input("Enter your query (or 'exit' to quit): ").strip().lower()

        if topic == 'exit':
            break

        result = fetch_and_summarize(topic)

        if result:
            print(result['summary'])
        else:
            print("No relevant information found.")'''