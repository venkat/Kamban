Kamban
======

Kamban is a simple tool for quantizing the creativity of given text content. This was written hurriedly in a couple of hours. It is a pretty naive tool.

### Notes

1. adjudge.py takes a english text file as input and calculates
counts needed to find the creativity index. it takes time as
it keeps downloading pages from wikipedia. redirect the output
of this code to a file.

    `python adjudge.py -i license_1.txt > result.txt`

2. quantize.py reads the result.txt from standard input and does the calculation and
prints the creativity index - last line of the output.

    `python quantize.py < result.txt`

3. to tweak the calculation, tweak the formula at the end of quantize.py

4. `license_1.txt` and `80days_3.txt` are sample test files and their respective
result files are names with the suffix results.txt

5. Thank you Vivake Gupta (v@nano.com) for the stemmer.py!

6. Tweet me @annacoder for feedback.

7. More details at http://venkat.io/posts/kamban-quantizing-creativity-of-written-content/
