#!/bin/bash
# fastq-merger 0.0.2
# Generated by dx-app-wizard.
#
# Basic execution pattern: Your app will run on a single machine from
# beginning to end.
#
# Your job's input variables (if any) will be loaded as environment
# variables before this script runs.  Any array inputs will be loaded
# as bash arrays.
#
# Any code outside of main() (or any entry point you may add) is
# ALWAYS executed, followed by running the entry point itself.
#
# See https://documentation.dnanexus.com/developer for tutorials on how
# to modify this file.

main() {

    echo "Value of fastq1: '$fastq1'"
    echo "Value of fastq2: '$fastq2'"
    echo "Value of fastq3: '$fastq3'"
    echo "Value of fastq4: '$fastq4'"
    echo "Value of fastq5: '$fastq5'"
    echo "Value of output_name_prefix: '$output_name_prefix'"

    # The following line(s) use the dx command-line tool to download your file
    # inputs to the local file system using variable names for the filenames. To
    # recover the original filenames, you can use the output of "dx describe
    # "$variable" --name".

    dx download "$fastq1" -o fastq1

    dx download "$fastq2" -o fastq2
    if [ -n "$fastq3" ]
    then
        dx download "$fastq3" -o fastq3
    fi
    if [ -n "$fastq4" ]
    then
        dx download "$fastq4" -o fastq4
    fi
    if [ -n "$fastq5" ]
    then
        dx download "$fastq5" -o fastq5
    fi
    VAR1=$output_name_prefix
    VAR2=".fastq.gz"
    VAR3=$VAR1$VAR2
    cat fastq* > $VAR3

    # Fill in your application code here.
    #
    # To report any recognized errors in the correct format in
    # $HOME/job_error.json and exit this script, you can use the
    # dx-jobutil-report-error utility as follows:
    #
    #   dx-jobutil-report-error "My error message"
    #
    # Note however that this entire bash script is executed with -e
    # when running in the cloud, so any line which returns a nonzero
    # exit code will prematurely exit the script; if no error was
    # reported in the job_error.json file, then the failure reason
    # will be AppInternalError with a generic error message.

    # The following line(s) use the dx command-line tool to upload your file
    # outputs after you have created them on the local file system.  It assumes
    # that you have used the output field name for the filename for each output,
    # but you can change that behavior to suit your needs.  Run "dx upload -h"
    # to see more options to set metadata.

    fastq_final=$(dx upload $VAR3 --brief)

    # The following line(s) use the utility dx-jobutil-add-output to format and
    # add output variables to your job's output as appropriate for the output
    # class.  Run "dx-jobutil-add-output -h" for more information on what it
    # does.

    dx-jobutil-add-output fastq_final "$fastq_final" --class=file
}
