#! /usr/bin/env python
# stats.py

"""Classes and functions for dealing with video statistics."""

import csv

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
    'quant'
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
        skipped = 0
        for line in csv_reader:
            # Convert some string and numeric fields
            try:
                line['format'] = str.lower(line['format'] or '')
                line['tvsys'] = str.lower(line['tvsys'] or '')
                line['length'] = int(line['length'] or 0)
                line['avg_bitrate'] = int(line['avg_bitrate'] or 0)
                line['tgt_bitrate'] = int(line['tgt_bitrate'] or 0)
                line['peak_bitrate'] = int(line['peak_bitrate'] or 0)
                line['encoding_time'] = int(line['encoding_time'] or 0)
            # If conversion failed, just skip this line
            except ValueError:
                skipped += 1
            # Conversion worked; append to current records
            else:
                self.records.append(line)

        statfile.close()
        print "Read %s lines from %s" % (len(self.records), filename)
        print "Skipped %s lines because they contained empty fields." % skipped

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
        values = []
        for record in self.records:
            values.append(record[attribute])
        if len(values) > 0:
            return float(sum(values) / len(values))
        else:
            return 0

    def average_by(self, attribute, by_attribute):
        """Return a dictionary of averages of an attribute, indexed by another
        attribute. For example, average_by('bitrate', 'format') returns average
        bitrates for each format."""
        values_by = self.list_by(attribute, by_attribute)
        # Calculate averages for each value-list
        averages = {}
        if len(values_by) > 0:
            for key, samples in values_by.iteritems():
                averages[key] = float(sum(samples) / len(samples))
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
            values_by[byval].append(record[attribute])
        if sort_lists:
            for index in values_by.iterkeys():
                values_by[index].sort()
        return values_by
    