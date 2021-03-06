import os


def clear_dir(work_dir, mkdir):
    # Empty the working directory
    # Currently done by deleting then (if desired) making it again
    os.system('rm -rf ' + work_dir)
    if mkdir:
        os.system('mkdir ' + work_dir)


def copy_file(trans_dir, work_dir, file):
    # Copy the jst file into the working directory
    os.system('cp ' + trans_dir + file + ' ' + work_dir)


def convert_to_image(img_dir, file):
    # Convert the jst file (presumably PDF) into an image (jpg) using imagemagick
    # Command for imagemagick version 6 is "convert-im6 inputfile -density (value) outputfile"
    # Higher density for higher quality, up to a certain point. Will take longer to run at higher values of course
    os.system('mkdir ' + img_dir)
    os.system('(cd ' + img_dir + '; convert-im6 -density 300 ../' + file + ' image' + '.jpg' + ')')


def read_and_scan(text_dir, num):
    saved_course = None
    course_list = []

    for i in range(0, num):
        print("Converting image to text.. ", i)
        read_command = '(cd ' + text_dir + '; tesseract ../image' + '-' + str(i) + '.jpg image' + '-' + str(i) + ')'
        os.system(read_command)
        filename = text_dir + 'image-' + str(i) + '.txt'

        print("Scanning text file.. ", i)
        for line in open(filename):
            if "Military Experience" in line:
                if saved_course is not None and saved_course not in course_list:
                    course_list.append(saved_course)
                return course_list
            if "Credit Is Not Recommended" in line:
                saved_course = None
            if 'MC-' in line or 'NV-' in line or 'AR-' in line or 'CG-' in line or 'AF-' in line or 'DD-' in line:
                for word in line.split():
                    if word.startswith('MC-') or word.startswith('NV-') or word.startswith('AR-') \
                            or word.startswith('CG-') or word.startswith('DD-') or word.startswith('AF-'):
                        if saved_course is not None and saved_course not in course_list:
                            course_list.append(saved_course)
                        saved_course = word
    return course_list


def grab_jst_courses(trans_dir, jst):
    working_dir = trans_dir + 'working/'
    image_dir = working_dir + 'images/'
    text_dir = image_dir + 'text/'

    clear_dir(working_dir, True)
    copy_file(trans_dir, working_dir, jst)
    convert_to_image(image_dir, jst)

    os.system('mkdir ' + text_dir)
    num_pages = int(os.popen('ls ' + image_dir + ' -1 | wc -l').read())

    course_list = read_and_scan(text_dir, num_pages)
    clear_dir(working_dir, False)
    return course_list


# Required variables are transcript directory, jst filename, and desired image name
# All others are generated by the functions above
transcript_dir = 'files/Transcripts/'
jst_files = ['C.Mott_JST_1.7.19.pdf', '1842_001.pdf', 'J.Saucedo_JST_Transcript.pdf']

print(grab_jst_courses(transcript_dir, jst_files[2]))
