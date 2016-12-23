'''
Created on Dec 21, 2016

@author: safdar
'''
import argparse

if __name__ == '__main__':
    print ("###############################################")
    print ("#                 TRANSFORMER                 #")
    print ("###############################################")

    parser = argparse.ArgumentParser(description='Image Transformer')
    parser.add_argument('-i', dest='input',    required=True, type=str, help='Path to distorted image file or distorted images folder.')
    parser.add_argument('-f', dest='output',   required=True, type=str, help='Location of output (Will be treated as the same as input type)')
    parser.add_argument('-b', dest='calibration',  required=True, type=str, help='Location of calibration file')
    parser.add_argument('-o', dest='overwrite', action='store_true', help='Overwrite output file(s) if they already exist (default: false)')
    parser.add_argument('-d', dest='dry', action='store_true', help='Dry run. Will not save anything to disk (default: false).')
    args = parser.parse_args()

    pass