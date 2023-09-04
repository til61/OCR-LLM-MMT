from main import perform_ocr, translate_text
import sys
import timeit

# open ended tests
def test_translation(text):
    print("Testing translation...")
    print(f"Input: {text}")
    result = translate_text(text, debug=True)
    print(f"Result: {result}")

def test_ocr(image):
    result = perform_ocr(image, debug=True)

def main():
    test_name = sys.argv[1]
    test_input = sys.argv[2]

    print(f"Running test: {test_name}")
    print(f"Input: {test_input}")

    if test_name == "ocr":
        test_ocr(test_input)
    elif test_name == "translation":
        test_translation(test_input)

if __name__ == "__main__":
    main()