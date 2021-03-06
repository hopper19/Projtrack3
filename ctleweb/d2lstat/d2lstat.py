#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
d2lstat.py

python d2lstat.py usage_data.csv full_time.csv part_time.csv semester_name number_of_courses_running

Given a correct data set and lists of full- and part-time teachers, this program will generate usage statistics on a
given template, which can be edited under the generate_document function.

Authors:
Dan Ricker <daniel.ricker@scranton.edu>
Sean Batzel <sean.batzel@scranton.edu>

This program is the property of the UofS-CTLE.
"""
from __future__ import division

import csv
import os

from django.conf import settings

# GLOBAL SETTINGS - DO NOT CHANGE UNLESS ABSOLUTELY NECESSARY.
DELIMITER = '|'  # Determines what character the program wil break data rows on.
ASSIGNMENTS = 13  # The column that assignments data is located in.
GRADE = 15  # The column that grade item data is located in.
GRADED = 16  # The column that graded grade item data is located in.
DISCUSSION = 18  # The column for discussion post usage.
USAGE_ROYAL = 3  # The column where the instructor's R number is located in the usage file.
FAC_ROYAL = 0  # Where the faculty member's R number is located in the full-/part-time CSV files.


def filter_for_semester(files_data, semester):
    """
    Used to filter the entire set of usage data for a given semester.

    :param files_data: The list of all course data taken from the usage CSV file.
    :param semester: The year and semester (e.g. 2018_Fall) to search for in the usage data.
    :return: The list of courses pertaining to the given semester.
    """
    final = list()
    for x in files_data:
        y = x.split(DELIMITER)
        if semester in y[9]:  # NOTE This will always work, provided the semester string is given correctly.
            final.append(x)
    return final


def get_rows_with_usage(files_data):
    """
    Filters the semester's courses on which ones had activity in D2L.

    :param files_data: The filtered list of courses for the semester.
    :return: The list of courses that had relevant usage in D2L.
    """
    final = list()
    for x in files_data:
        y = x.split(DELIMITER)
        if int(y[ASSIGNMENTS]) > 0 or int(y[GRADE]) > 2 or int(y[GRADED]) > 0 or int(y[DISCUSSION]) > 0:
            final.append(x)
    return final


def remove_duplicate_crn(files_data):
    """
    Makes sure that none of the courses in the list repeat.

    :param files_data: Filtered data passed in from get_rows_with_usage.
    :return: The list of coures without any repeated.
    """
    seen_crns = []
    ret_val = []
    for x in files_data:
        y = x.split(DELIMITER)
        # This checks the last 5 characters of y[9] for a CRN.
        # Make sure this is where the CRN is still located before running.
        if y[9][-5:] not in seen_crns:
            seen_crns.append(y[9][-5:])
            ret_val.append(x)
    return ret_val


def remove_duplicate_royal(files_data):
    """
    Filters and removes duplicate instructor RIDs.

    :param files_data: Filtered data passed in from get_rows_with_usage.
    :return: The list of courses with no instructor R numbers duplicated.
    """
    seen_royal = []
    ret_val = []
    for x in files_data:
        y = x.split(DELIMITER)
        if y[USAGE_ROYAL] not in seen_royal:
            seen_royal.append(y[USAGE_ROYAL])
            ret_val.append(x)
    return ret_val


def parse_files(usage, full_time, part_time, semester, total_courses):
    """
    Reads the given CSV files and splits up the contents into digestible data structures.

    :param usage: The name of the usage CSV file.
    :param full_time: The name of the CSV of full-time faculty members.
    :param part_time: The name of the CSV of part-time faculty members.
    :param semester: The semester in the form YYYY_Session (e.g. 2018_Fall).
    :param total_courses: (Provided externally) The number of courses running for the given semester.
    :return: A data structure containing all of the data required for the rest of the program.
    """
    with open(usage, mode='rU') as infile:
        reader = csv.reader(infile, dialect='excel', delimiter=',', quotechar='"')
        rows = list()
        for row in reader:
            rows.append(row)
        with open(usage, mode='w') as outfile:
            writer = csv.writer(outfile, delimiter=DELIMITER)
            writer.writerows(rows)
    with open(full_time, mode='rU') as infile:
        reader = csv.reader(infile, dialect='excel', delimiter=',', quotechar='"')
        rows = list()
        for row in reader:
            rows.append(row)
        with open(full_time, mode='w') as outfile:
            writer = csv.writer(outfile, delimiter=DELIMITER)
            writer.writerows(rows)
    with open(part_time, mode='rU') as infile:
        reader = csv.reader(infile, dialect='excel', delimiter=',', quotechar='"')
        rows = list()
        for row in reader:
            rows.append(row)
        with open(part_time, mode='w') as outfile:
            writer = csv.writer(outfile, delimiter=DELIMITER)
            writer.writerows(rows)
    one = filter_for_semester(open(usage, 'r').readlines(), semester)
    two = get_rows_with_usage(one)
    usage_file = remove_duplicate_crn(two)
    no_dup_r = remove_duplicate_royal(two)
    full_time_file = open(full_time, 'r').readlines()
    full_r = list()
    part_r = list()
    for x in full_time_file:
        y = x.split(DELIMITER)
        full_r.append(y[FAC_ROYAL])
    part_time_file = open(part_time, 'r').readlines()
    for x in part_time_file:
        y = x.split(DELIMITER)
        part_r.append(y[FAC_ROYAL])
    full = list()
    part = list()
    staff = list()
    for x in range(len(part_r)):
        part_r[x] = part_r[x].strip("\"")
    for x in range(len(full_r)):
        full_r[x] = full_r[x].strip("\"")
    for x in no_dup_r:
        y = x.split(DELIMITER)
        if y[USAGE_ROYAL] in full_r:
            full.append(y)
        elif y[USAGE_ROYAL] in part_r:
            part.append(y)
        else:
            staff.append(y)
    return {'semester_no_dup_crn': usage_file,
            'semester_no_dup_r': no_dup_r,
            'semester': two,
            'full_time': full,
            'len_full': len(full_time_file),
            'part_time': part,
            'len_part': len(part_time_file),
            'staff': staff,
            'total_courses': total_courses}


def calculate_stats(file_data):
    """
    Carries out the actual logic for generating the numbers that will be included in the report.

    :param file_data: The data produced by the parse function.
    :return: The statistics data required for the report generator.
    """
    specifics = {
        'assignments': 0,
        'grade': 0,
        'graded': 0,
        'discussion': 0
    }
    for course in file_data['semester_no_dup_crn']:
        x = course.split(DELIMITER)
        if int(x[ASSIGNMENTS]) > 0:
            specifics['assignments'] += 1
        if int(x[GRADE]) > 2:
            specifics['grade'] += 1
        if int(x[GRADED]) > 0:
            specifics['graded'] += 1
        if int(x[DISCUSSION]) > 0:
            specifics['discussion'] += 1
    return {'semester': file_data['semester'],
            'courses_with_usage': len(file_data['semester_no_dup_crn']),
            'faculty_with_usage': len(file_data['semester_no_dup_r']),
            'full_time': len(file_data['full_time']),
            'total_full_time': file_data['len_full'],
            'part_time': len(file_data['part_time']),
            'total_part_time': file_data['len_part'],
            'staff': len(file_data['staff']),
            'specifics': specifics,
            'total_courses': file_data['total_courses']}


def generate_document(stats, semester):
    """
    Generates an HTML document and PDF with the requested stats for the semester's D2L usage.

    :param stats: The dictionary returned by the generate_stats function.
    :param semester: The semester value passed in as a command-line argument.
    """
    with open(os.path.join(settings.BASE_DIR, 'd2lstat/templates/d2lstat/raw_html.html'), 'r') as f:
        string = f.read()
    string = string.format(semester,
                           stats['faculty_with_usage'],
                           stats['full_time'],
                           stats['total_full_time'],
                           round((stats['full_time'] / stats['total_full_time']) * 100, 1),
                           stats['part_time'],
                           stats['total_part_time'],
                           round((stats['part_time'] / stats['total_part_time']) * 100, 1),
                           stats['staff'],
                           stats['courses_with_usage'],
                           stats['total_courses'],
                           round((stats['courses_with_usage'] / int(stats['total_courses'])) * 100, 1),
                           stats['specifics']['assignments'],
                           stats['specifics']['grade'],
                           stats['specifics']['graded'],
                           stats['specifics']['discussion'])
    with open(os.path.join(settings.BASE_DIR, 'd2lstat/templates/d2lstat/report.html'), 'w') as f:
        f.write(string)
        f.close()


def process_file(usage, full_time, part_time, semester, total_courses):
    """

    :param usage:
    :param full_time:
    :param part_time:
    :param total_courses
    :param semester:
    """
    res = parse_files(usage, full_time, part_time, semester, total_courses)
    res = calculate_stats(res)
    generate_document(res, semester)


def calculateVirtualClassroomStats(usage, fullTime, partTime, VCDataFile):
    resultList = []
    # read in the data from the lti (learning tools integration) file
    virtualClassroomDataFile = open(VCDataFile, 'rU')
    virtualClassroomDataReader = csv.reader(virtualClassroomDataFile)
    virtualClassroomData = []
    seenVirtualClassRoomOrgUnitIds = []
    for row in virtualClassroomDataReader:
        if ('youseeu' in row[5] and row[
            1] not in seenVirtualClassRoomOrgUnitIds):  # get the org unit ids of the courses in which there was created at least one virtual classroom meeting
            virtualClassroomData.append(row)
            seenVirtualClassRoomOrgUnitIds.append(row[1])
    # read in the instructor usage data file that was obtained from desire 2 learn data hub
    instructorUsageDataFile = open(usage, 'rU')
    instructorUsageDataReader = csv.reader(instructorUsageDataFile)
    instructorUsageData = []
    seenRIds = []
    numberOfFacultyMembersUsingVirtualClassroom = 0
    fullDataOnInstructors = []
    # print('Instructors That Have Created at Least 1 Virtual Classroom Meeting:')
    resultList.append('Instructors That Have Created at Least 1 Virtual Classroom Meeting:')
    for row in instructorUsageDataReader:
        if (row[
            10] in seenVirtualClassRoomOrgUnitIds):  # filter the rows to just be the rows for faculty members that have created at least one virtual classroom meeting
            if (row[3] not in seenRIds):  # make sure that each instructor is onlt accounted for once
                seenRIds.append(row[3])
                fullDataOnInstructors.append([row[3], row[1], row[2]])
                # print(row[3] + ': ' + row[1] + ', ' + row[2])
                resultList.append(row[3] + ': ' + row[1] + ', ' + row[2])
    numberOfFacultyMembersUsingVirtualClassroom = len(seenRIds)

    # print('Number of Instructors That Have Created at Least 1 Virtual Classroom Meeting: ' + str(
    #     numberOfFacultyMembersUsingVirtualClassroom))
    resultList.append('Number of Instructors That Have Created at Least 1 Virtual Classroom Meeting: ' + str(
        numberOfFacultyMembersUsingVirtualClassroom))
    seenFullAndPartTimeRIds = []  # this is needed to keep track of the Rids that belong to either full or part time faculty members in order to determine which rids are left over, the left over rids are the rids of staff members teaching part time
    # Full time faculty members that have created at least one virtual classroom meeting
    fullTimeFacultyDataFile = open(fullTime, 'rU')
    fullTimeFacultyDataReader = csv.reader(fullTimeFacultyDataFile)
    fullTimeFacultyUsingVirtualClassroomRids = []
    for row in fullTimeFacultyDataReader:
        if (row[0] in seenRIds):
            fullTimeFacultyUsingVirtualClassroomRids.append(row[0])
            seenFullAndPartTimeRIds.append(row[0])
    # Part time faculty members that have created at least one virtual classroom meeting
    partTimeFacultyDataFile = open(partTime, 'rU')
    partTimeFacultyDataReader = csv.reader(partTimeFacultyDataFile)
    partTimeFacultyUsingVirtualClassroomRids = []
    for row in partTimeFacultyDataReader:
        if (row[0] in seenRIds):
            partTimeFacultyUsingVirtualClassroomRids.append(row[0])
            seenFullAndPartTimeRIds.append(row[0])
    staffTeachingPartTimeRids = []
    for rid in seenRIds:
        if (rid in seenFullAndPartTimeRIds):
            staffTeachingPartTimeRids.append(rid)
    # sort full instructor data based upon the rids in each category
    fullTimeFacultyUsingVC = []
    partTimeFacultyUsingVC = []
    staffUsingVC = []
    # sort out full time faculty
    for rid in fullTimeFacultyUsingVirtualClassroomRids:
        for row in fullDataOnInstructors:
            if (row[0] == rid):
                fullTimeFacultyUsingVC.append(row)
    # sort out part time faculty
    for rid in partTimeFacultyUsingVirtualClassroomRids:
        for row in fullDataOnInstructors:
            if (row[0] == rid):
                partTimeFacultyUsingVC.append(row)
    # sort out staff
    for row in fullDataOnInstructors:
        if (row[0] not in seenFullAndPartTimeRIds):
            staffUsingVC.append(row)
    resultList.append("Full Time Faculty Using Virtual Classroom:")
    # print("Full Time Faculty Using Virtual Classroom:")
    for row in fullTimeFacultyUsingVC:
        # print(row[0] + ': ' + row[2] + ', ' + row[1])
        resultList.append(row[0] + ': ' + row[2] + ', ' + row[1])

    # print("The Number of Full Time Faculty Using Virtual Classroom: " + str(len(fullTimeFacultyUsingVC)))
    resultList.append("The Number of Full Time Faculty Using Virtual Classroom: " + str(len(fullTimeFacultyUsingVC)))
    # print("Part Time Faculty Using Virtual Classroom:")
    resultList.append("Part Time Faculty Using Virtual Classroom:")
    for row in partTimeFacultyUsingVC:
        # print(row[0] + ': ' + row[2] + ', ' + row[1])
        resultList.append(row[0] + ': ' + row[2] + ', ' + row[1])
    # print("The Number of Part Time Faculty Using Virtual Classroom: " + str(len(partTimeFacultyUsingVC)))
    resultList.append("The Number of Part Time Faculty Using Virtual Classroom: " + str(len(partTimeFacultyUsingVC)))
    # print("Staff Teaching Part Time Using Virtual Classroom:")
    resultList.append("Staff Teaching Part Time Using Virtual Classroom:")
    for row in staffUsingVC:
        # print(row[0] + ': ' + row[2] + ', ' + row[1])
        resultList.append(row[0] + ': ' + row[2] + ', ' + row[1])
    print("The Number of Staff Teaching Part Time Using Virtual Classroom: " + str(len(staffUsingVC)))
    resultList.append("The Number of Staff Teaching Part Time Using Virtual Classroom: " + str(len(staffUsingVC)))
    return resultList

def facultyNotUsingD2LCalculation(usage, fullTime, partTime, semester):
    resultList = []
    usageFile = open(usage, 'rU')
    fullTimeFile = open(fullTime, 'rU')
    partTimeFile = open(partTime, 'rU')
    usageFileReader = csv.reader(usageFile)
    fullTimeFileReader = csv.reader(fullTimeFile)
    partTimeFileReader = csv.reader(partTimeFile)
    usageDataRaw = []
    usageData = []
    fullTimeDataRaw = []
    partTimeDataRaw = []
    fullTimeNotUsing = []
    partTimeNotUsing = []
    staffTeachingPartTimeNotUsing = []
    fullTimeRIds = []
    partTimeRIds = []
    ridsOfInstructorsUsing = []
    seenRidsOfInstructorsUsing = []
    ridsOfInstructorsUsingDuplicatesRemoved = []
    # read in the usage data
    for row in usageFileReader:
        usageDataRaw.append(row)
    # Get the rids of the instructors using D2L
    for row in usageDataRaw:
        # print(row[13] + ',' +row[15] + ',' +row[16] + ',' +row[18])
        try:
            if((int(row[13])>0 or int(row[15])>2 or int(row[16])>0 or int(row[18])>0)):
                if(semester in row[9]):
                    ridsOfInstructorsUsing.append(row[3])
        except Exception:
            print(Exception)
    seenRIds = []
    # Filter the rids of instuctors using for duplicates
    for row in ridsOfInstructorsUsing:
        if(row not in seenRidsOfInstructorsUsing):
            ridsOfInstructorsUsingDuplicatesRemoved.append(row)
            seenRidsOfInstructorsUsing.append(row)
    #get the Rids of instructors not using
    for row in usageDataRaw:
        if(row[3] not in ridsOfInstructorsUsingDuplicatesRemoved and semester in row[9]):
            usageData.append(row)
    for row in fullTimeFileReader:
        fullTimeDataRaw.append(row)
    for row in partTimeFileReader:
        partTimeDataRaw.append(row)
    for row in fullTimeDataRaw:
        fullTimeRIds.append(row[0])
    for row in partTimeDataRaw:
        partTimeRIds.append(row[0])
    for row in usageData:
        if(row[3] in fullTimeRIds and row[3] not in seenRIds):
            fullTimeDepartment = ''
            for fullTimeRow in fullTimeDataRaw:
                if(row[3]==fullTimeRow[0]):
                    fullTimeDepartment = fullTimeRow[5]
            fullTimeNotUsing.append([row[3], row[1], row[2], fullTimeDepartment])
            seenRIds.append(row[3])
        elif(row[3] in partTimeRIds and row[3] not in seenRIds):
            if(row[3] in partTimeRIds):
                partTimeDepartment = ''
                for partTimeRow in partTimeDataRaw:
                    if(row[3]==partTimeRow[0]):
                        partTimeDepartment = partTimeRow[5]
                partTimeNotUsing.append([row[3], row[1], row[2], partTimeDepartment])
                seenRIds.append(row[3])
        else:
            if(row[3] not in seenRIds):
                staffTeachingPartTimeNotUsing.append([row[3], row[1], row[2]])
                seenRIds.append(row[3])
    resultList.append('The Total Number of Faculty Not Using Desire 2 Learn: ' + str(len(fullTimeNotUsing)+len(partTimeNotUsing) + len(staffTeachingPartTimeNotUsing)))
    resultList.append('The Number of Full Time Faculty Not Using D2L: ' + str(len(fullTimeNotUsing)))
    resultList.append('Full Time Faculty Not Using Desire 2 Learn:')
    for row in fullTimeNotUsing:
        resultList.append(row[0] + ', ' + row[1] + ', ' + row[2] + ', ' + row[3])
    resultList.append('')
    resultList.append('')
    resultList.append('The Number of Part Time Faculty Not Using D2L: ' + str(len(partTimeNotUsing)))
    resultList.append('Part Time Faculty Not Using Desire 2 Learn:')
    for row in partTimeNotUsing:
        resultList.append(row[0] + ', ' + row[1] + ', ' + row[2] + ', ' + row[3])
    resultList.append('')
    resultList.append('')
    resultList.append(
        'The Number of Staff Teaching Part Time Faculty Not Using D2L: ' + str(len(staffTeachingPartTimeNotUsing)))
    resultList.append('Staff Teaching Part Time Not Using Desire 2 Learn:')
    for row in staffTeachingPartTimeNotUsing:
        resultList.append(row[0] + ', ' + row[1] + ', ' + row[2])
    return resultList