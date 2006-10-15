#! /usr/bin/env python
# stats.py

"""Classes and functions for dealing with video statistics."""

import csv
import sys

# Order of fields in stats.tovid
fields = [\
    'tovid_version',
    'final_name',
    'length',          # a.k.a. CUR_LENGTH
    'format',          # RES
    'tvsys',
    'final_size',
    'tgt_bitrate',
    'avg_bitrate',
    'peak_bitrate',
    'gop_minsize',
    'gop_maxsize',
    'encoding_time',   # SCRIPT_TOT_TIME
    'cpu_model',
    'cpu_speed',
    'in_vcodec',
    'in_acodec',
    'encoding_mode',
    'in_md5',
    'in_width',
    'in_height',
    'quant',
    'kbpm',
    'enc_time_ratio',
    'backend'
    ]

# Integer numeric fields
int_fields = [\
    'length',
    'avg_bitrate',
    'tgt_bitrate',
    'peak_bitrate',
    'encoding_time',
    'final_size',
    'cpu_speed',
    'in_width',
    'in_height',
    'quant',
    'kbpm'
    ]

class Statlist:
    """A list of statistics that may be queried with a simple database-like
    interface."""
    def __init__(self, filename=''):
        """Create a Statlist, reading from the given filename."""
        self.records = []
        if filename is not '':
            self.read_csv(filename)

    def read_csv(self, filename):
        """Import stats from a CSV (comma-delimited quoted text) file."""
        self.records = []
        statfile = open(filename, 'r')
        csv_reader = csv.DictReader(statfile, fields, skipinitialspace=True)
        for line in csv_reader:
            # Convert some string and numeric fields
            line['format'] = str.lower("%s" % line['format'])
            line['tvsys'] = str.lower("%s" % line['tvsys'])
            for field in int_fields:
                try:
                    num = int("%s" % line[field])
                except ValueError, TypeError:
                    num = 0
                line[field] = num
            self.records.append(line)

        statfile.close()
        print "Read %s lines from %s" % (len(self.records), filename)

    def unique(self, field):
        """Return a list of unique values of the given field."""
        unique_values = []
        for record in self.records:
            if record[field] not in unique_values:
                unique_values.append(record[field])
        return unique_values

    def count_unique(self, field):
        """Count the occurrences of each unique value of the given field.
        Return a dictionary of unique values and the number of occurrences
        of each."""
        counts = {}
        # Go through all records and total up occurrences of each value
        for record in self.records:
            value = record[field]
            if value is None or value == '':
                pass
            elif value not in counts:
                counts[value] = 1
            else:
                counts[value] += 1
        return counts
        
    def average(self, attribute):
        """Calculate the average value for a given numeric VidStat attribute.
        For example, average('bitrate') returns the average overall bitrate of
        all videos in the list."""
        # Error if attribute is non-numeric
        if attribute not in int_fields:
            print "Can't average %s: not defined as a numeric field"
            sys.exit()
            
        values = []
        for record in self.records:
            # Only append non-zero values
            if record[attribute] != 0:
                values.append(record[attribute])
        if len(values) > 0:
            return float(sum(values) / len(values))
        else:
            return 0

    def average_by(self, attribute, by_attribute):
        """Return a dictionary of averages of an attribute, indexed by another
        attribute. For example, average_by('bitrate', 'format') returns average
        bitrates for each format."""
        # Error if attribute is non-numeric
        if attribute not in int_fields:
            print "Can't average %s: not defined as a numeric field"
            sys.exit()

        values_by = self.list_by(attribute, by_attribute)
        # Calculate averages for each value-list
        averages = {}
        if len(values_by) > 0:
            for key, samples in values_by.iteritems():
                try:
                    averages[key] = float(sum(samples) / len(samples))
                except ZeroDivisionError:
                    averages[key] = 0.0
        return averages

    def list_by(self, attribute, by_attribute, sort_lists=False):
        """Return a dictionary of lists of values of the given attribute,
        indexed by another attribute. If sort_lists is True, sort all lists."""
        # Create a dictionary of value-lists, indexed by by_attribute
        values_by = {}        
        for record in self.records:
            byval = record[by_attribute]
            if not values_by.has_key(byval):
                values_by[byval] = []
            # Only include non-zero values
            if record[attribute] != 0:
                values_by[byval].append(record[attribute])
        if sort_lists:
            for index in values_by.iterkeys():
                values_by[index].sort()
        return values_by
    
    def get_matching(self, attribute, value):
        """Return a list of records where the given attribute equals the given
        value. Records are field-indexed dictionaries of values.
        """
        # List of matching records
        matches = []
        for record in self.records:
            if record[attribute] == value:
                matches.append(record)
        return matches
    
