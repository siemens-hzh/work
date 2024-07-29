import os


if __name__ == '__main__':
    import sys
    input, output = sys.argv[1:]
    for folder in os.listdir(input):
        cur_folder = os.path.join(input, folder)
        output_folder = os.path.join(output, folder)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        os.system(f"TotalSegmentator -i {cur_folder} -o {output}")
