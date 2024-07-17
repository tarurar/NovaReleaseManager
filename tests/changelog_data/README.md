# Test data for function `extract_latest_release_notes` from module `text_utils`

This directory contains test cases for the `extract_latest_release_notes` function. Each test case is stored in a separate plain text file and contains both the original changelog text and the expected output.

## File Format

Each test case file is formatted as follows:

1. The original changelog text.
2. A separator line consisting of three equal signs (`===`).
3. The expected output after processing the changelog text with the `extract_latest_release_notes` function.

## Example

Here is an example of a test case file:

```
## 2.63.0
### What's changed
* LT-5501: Filter allowed tab for standard layout.
* LT-5380: Migrate from bitbucket to github.
* LT-5376: Switch to nuget packages for math and security projects.
* LT-5172: Refactor watchlists.

## 2.62.0
### What's changed
* LT-5366: Add app header to logs
===
### What's changed
* LT-5501: Filter allowed tab for standard layout.
* LT-5380: Migrate from bitbucket to github.
* LT-5376: Switch to nuget packages for math and security projects.
* LT-5172: Refactor watchlists.
```

## Usage

The test cases are read by the test suite and used to verify the correctness of the `extract_latest_release_notes` function. Each test case file is processed to extract the original changelog text and the expected output, and the function's output is compared to the expected output.

## Adding New Test Cases

To add a new test case:
1. Create a new plain text file following the same format described above.
2. Save the file in this directory (`changelog_data`).
3. Add the new test case file to the `test_files` variable in `test_changelog_text_extraction.py`:

```python
test_files = [
    'changelog_data/test_case1.txt',
    'changelog_data/test_case2.txt',
    'changelog_data/test_case3.txt',
    'changelog_data/test_case4.txt',
    'changelog_data/test_case5.txt',
    'changelog_data/test_case6.txt',
    'changelog_data/new_test_case.txt'  # Add your new test case file here
]
```

## Test Files

- `test_case1.txt`
- `test_case2.txt`
- `test_case3.txt`
- `test_case4.txt`
- `test_case5.txt`
- `test_case6.txt`

Feel free to add more test case files following the same format to extend the test coverage.