import os
import sys
import collections
import PyPDF2
from ebooklib import epub
from bs4 import BeautifulSoup
import re
import random

def get_original_text_length_and_formatting(original_text):
    """
    Calculate the approximate length of the original text based on the word counts,
    extract punctuation, and capture positions of paragraphs and line breaks.
    """
    punctuation_marks = re.findall(r'[^\w\s]', original_text)
    paragraphs = original_text.split('\n\n')
    line_breaks = [match.start() for match in re.finditer(r'\n', original_text)]
    return len(original_text), punctuation_marks, paragraphs, line_breaks

def reconstruct_text(word_count_file, original_text):
    """
    Reconstruct the text based on word frequencies, original text length,
    and randomly add the same amount of punctuation, paragraphs, and line breaks as in the original text.
    Ensures that line breaks are inserted only between words.
    """
    word_frequencies = {}
    
    # Read word frequencies from the word count file
    try:
        with open(word_count_file, 'r', encoding='utf-8') as f:
            for line in f:
                word, count = line.strip().split(': ')
                word_frequencies[word] = int(count)
    except Exception as e:
        print(f"Error reading word count file: {e}")
        return ""
    
    # Extract formatting information from the original text
    original_text_length, punctuation_marks, paragraphs, line_breaks = get_original_text_length_and_formatting(original_text)
    
    # Create a list of words based on their frequencies
    reconstructed_text = []
    for word, count in word_frequencies.items():
        reconstructed_text.extend([word] * count)
    
    # Shuffle the list of words to randomize their order
    random.shuffle(reconstructed_text)
    
    # Randomly insert punctuation marks into the text
    for mark in punctuation_marks:
        insert_position = random.randint(0, len(reconstructed_text))
        reconstructed_text.insert(insert_position, mark)
    
    # Convert the list back into a string to add paragraphs and line breaks
    reconstructed_text_str = ' '.join(reconstructed_text)
    
    # Insert line breaks between words
    for _ in line_breaks:
        words = reconstructed_text_str.split(' ')
        if len(words) > 1:
            insert_position = random.randint(1, len(words) - 1)
            words.insert(insert_position, '\n')
            reconstructed_text_str = ' '.join(words)
    
    # Insert paragraphs (assuming paragraphs are separated by double newlines)
    for _ in range(len(paragraphs) - 1):
        words = reconstructed_text_str.split(' ')
        if len(words) > 1:
            insert_position = random.randint(1, len(words) - 1)
            words.insert(insert_position, '\n\n')
            reconstructed_text_str = ' '.join(words)
    
    # Trim the reconstructed text to match the original text length
    if len(reconstructed_text_str) > original_text_length:
        reconstructed_text_str = reconstructed_text_str[:original_text_length]
    
    return reconstructed_text_str

def extract_text_from_pdf():
    text = ''
    while True:
        file_path = input("Enter the path of the PDF file: ").strip()
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text()
            break  # Exit the loop if no error occurs
        except Exception as e:
            print(f"Error reading PDF file: {e}. Please try again.")
    return text, file_path


def extract_text_from_epub():
    text = ''
    while True:
        file_path = input("Enter the path of the EPUB file: ").strip()
        try:
            book = epub.read_epub(file_path)
            for item in book.get_items():
                if item.get_type() == epub.ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_body_content(), 'html.parser')
                    text += soup.get_text()
            break  # Exit the loop if no error occurs
        except Exception as e:
            print(f"Error reading EPUB file: {e}. Please try again.")
    return text, file_path


def load_excluded_words(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            excluded_words = set(word.strip().lower() for word in f.readlines())
    except Exception as e:
        print(f"Error reading excluded words file: {e}")
        excluded_words = set()
    return excluded_words


def count_words(text, excluded_words):
    words = re.findall(r'\b\w+\b', text.lower())
    filtered_words = [word for word in words if word not in excluded_words]
    word_counts = collections.Counter(filtered_words)
    return word_counts


def write_to_file(original_file_path, word_counts):
    base_name = os.path.splitext(os.path.basename(original_file_path))[0]
    output_file = f"{base_name}_word_count.txt"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for word, count in word_counts.most_common():
                f.write(f"{word}: {count}\n")
        print(f"Word count information has been written to {output_file}")
    except Exception as e:
        print(f"Error writing to file: {e}")
    return output_file


def save_reconstructed_text(original_file_path, reconstructed_text):
    base_name = os.path.splitext(os.path.basename(original_file_path))[0]
    output_file = f"{base_name}_reconstructed.txt"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(reconstructed_text)
        print(f"Reconstructed text has been written to {output_file}")
    except Exception as e:
        print(f"Error writing reconstructed text to file: {e}")


def main():
    file_type = input("Enter the type of file (pdf/epub): ").strip().lower()
    
    if file_type == 'pdf':
        text, file_path = extract_text_from_pdf()
    elif file_type == 'epub':
        text, file_path = extract_text_from_epub()
    else:
        print("Unsupported file type. Please provide a PDF or EPUB file.")
        sys.exit(1)

    excluded_words_file = 'excluded.txt'
    excluded_words = load_excluded_words(excluded_words_file)

    word_counts = count_words(text, excluded_words)
    for word, count in word_counts.most_common():
        print(f"{word}: {count}")

    save_to_file = input("Would you like this information written to a text file? y/n: ").strip().lower()
    if save_to_file == 'y':
        output_file = write_to_file(file_path, word_counts)
        
        reconstruct = input("Would you like to reconstruct the text? y/n: ").strip().lower()
        if reconstruct == 'y':
            reconstructed_text = reconstruct_text(output_file, text)
            
            save_reconstructed = input("Would you like to save the reconstructed text? y/n: ").strip().lower()
            if save_reconstructed == 'y':
                save_reconstructed_text(file_path, reconstructed_text)


if __name__ == "__main__":
    main()