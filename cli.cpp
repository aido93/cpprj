
#include <iostream>
#include <string>
#include <stdlib.h>
#include <getopt.h>

/**
 * \brief help function
 * \details print help on the screen
 */
void help()
{
	std::cout<<"$prj_name version $ver\n";
	std::cout<<"$desc\n";
	std::cout<<"Author: $auth\n";
	std::cout<<"Build date: $d\n";
	std::cout<<"Options:\n";
	std::cout<<"--help\t -h - print this help\n";
	std::cout<<"--input\t -i - input filename\n";
	std::cout<<"--output\t -i - output filename. if no or \"-\" then output will be on the screen"<<std::endl;
}

int main (int argc, char **argv)
{
	int c;
	std::string input_filename;
	std::string output_filename="-";
	static struct option long_options[] =
	{
	    {"help",    no_argument,       0, 'h'},
	    /* These options don’t set a flag.
	       We distinguish them by their indices. */
	    {"input",   required_argument, 0, 'i'},
	    {"output",  required_argument, 0, 'o'},
	    {0, 0, 0, 0}
	};
    while (1)
    {
	/* getopt_long stores the option index here. */
	int option_index = 0;

	c = getopt_long (argc, argv, "hi:o:",
					long_options, &option_index);

	/* Detect the end of the options. */
	if (c == -1)
		break;

	switch (c)
	{
		case 'h':
		help();
		exit(0);
		break;

		case 'i':
		input_filename=optarg;
		break;

		case 'o':
		output_filename=optarg;
		break;

		default:
		abort ();
	}
    }

	/* Print any remaining command line arguments (not options). */
	if (optind < argc)
	{
	 std::cout<<"non-option ARGV-elements: "<<std::endl;
	 while (optind < argc)
	    std::cout<<argv[optind++];
	 std::cout<<std::endl;
	}
	
	exit (0);
}
