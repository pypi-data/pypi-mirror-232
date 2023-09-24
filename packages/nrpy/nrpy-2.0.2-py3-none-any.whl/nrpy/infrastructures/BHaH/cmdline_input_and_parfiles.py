"""
Functions for parsing command-line input and parameter files.

Author: Zachariah B. Etienne
        zachetie **at** gmail **dot* com
"""

from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
import nrpy.c_function as cfc
import nrpy.params as par


def register_CFunction_cmdline_input_and_parfile_parser(
    project_name: str,
    cmdline_inputs: Optional[List[str]] = None,
) -> None:
    """
    Register a C function to handle command-line input and parse parameter files for a given project.

    This function defines and registers a series of C functions and constants that facilitate reading
    and parsing parameter files containing key-value pairs. It supports handling whitespace and comments,
    and has specific error handling for buffer overflows, invalid integers, and invalid doubles.

    It also incorporates various usage options for handling command-line arguments and integrates
    steerable parameters that can be overwritten from the command line.

    :param project_name: Name of the project. Used for file naming and error messaging.
    :param cmdline_inputs: Optional list of command-line inputs that can be used to overwrite specific
                           parameters defined in the parameter file.
    """
    num_commondata_params = 0
    for CodeParam in par.glb_code_params_dict.values():
        if CodeParam.commondata and CodeParam.add_to_parfile:
            num_commondata_params += 1
    prefunc = f"#define NUM_PARAMETERS {num_commondata_params} // Define the number of parameters"
    prefunc += r"""
#define LINE_SIZE 1024 // Define the max size of a line
#define PARAM_SIZE 128 // Define the max param string size

static char* trim_space(char *str) {
    char *end;

    // Trim leading spaces
    while (isspace((unsigned char)*str)) str++;

    // Trim trailing spaces
    end = str + strlen(str) - 1;
    while (end > str && isspace((unsigned char)*end)) end--;

    *(end + 1) = '\0';

    return str;
}

static void safe_copy(char *dest, const char *src, size_t size) {
  if (strlen(src) >= size) {
    fprintf(stderr, "Error: Buffer overflow detected.\n");
    exit(1);
  }
  strcpy(dest, src);
}

static void read_integer(const char *value, int *result, const char *param_name) {
  char *endptr;
  errno = 0; // To detect overflow
  long int_val = strtol(value, &endptr, 10);

  if (endptr == value || *endptr != '\0' || errno == ERANGE) {
    fprintf(stderr, "Error: Invalid integer value for %s: %s.\n", param_name, value);
    exit(1);
  }

  *result = (int)int_val;
}

static void read_double(const char *value, double *result, const char *param_name) {
  char *endptr;
  errno = 0; // To detect overflow
  double double_val = strtod(value, &endptr);

  if (endptr == value || *endptr != '\0' || errno == ERANGE) {
    fprintf(stderr, "Error: Invalid double value for %s: %s.\n", param_name, value);
    exit(1);
  }

  *result = double_val;
}

static void read_chararray(const char *value, char *result, const char *param_name, size_t size) {
  // Validation logic for string if necessary (e.g., length or format checks)

  if (strlen(value) >= size) {
    fprintf(stderr, "Error: Buffer overflow detected for %s.\n", param_name);
    exit(1);
  }

  strcpy(result, value);
}
"""
    if cmdline_inputs is None:
        cmdline_inputs = []
    list_of_steerable_params_str = " ".join(cmdline_inputs)
    prefunc += rf"""// Function to print usage instructions
static void print_usage() {{
  fprintf(stderr, "Usage option 0: ./{project_name} [--help or -h] <- Outputs this usage command\n");
  fprintf(stderr, "Usage option 1: ./{project_name} <- reads in parameter file {project_name}.par\n");
  fprintf(stderr, "Usage option 2: ./{project_name} [parfile] <- reads in parameter file [parfile]\n");
  fprintf(stderr, "Usage option 3: ./{project_name} [{list_of_steerable_params_str}] <- overwrites parameters in list after reading in {project_name}.par\n");
  fprintf(stderr, "Usage option 4: ./{project_name} [parfile] [{list_of_steerable_params_str}] <- overwrites list of steerable parameters after reading in [parfile]\n");
}}"""
    includes = ["BHaH_defines.h", "<string.h>", "<ctype.h>", "<errno.h>"]
    desc = r"""AUTOMATICALLY GENERATED BY parameter_file_read_and_parse.py
parameter_file_read_and_parse() function:
Reads and parses a parameter file to populate commondata_struct commondata.

This function takes in the command-line arguments and a pointer to a commondata_struct.
It reads the provided file and extracts the parameters defined in the file, populating
the commmondata_struct with the values. The file is expected to contain key-value pairs
separated by an equals sign (=), and it may include comments starting with a hash (#).
The function handles errors such as file opening failure, duplicate parameters, and
invalid parameter names.

@param griddata_params: Pointer to the commondata struct to be populated.
@param argc: The argument count from the command-line input.
@param argv: The argument vector containing command-line arguments."""

    c_type = "void"
    name = "cmdline_input_and_parfile_parser"
    params = "commondata_struct *restrict commondata, int argc, const char *argv[]"
    if cmdline_inputs is None:
        cmdline_inputs = []
    body = f"const int number_of_steerable_parameters = {len(cmdline_inputs)};\n"
    body += rf"""
  int option;

  // Check for "-h" or "--help" options
  if (argc == 2 && (strcmp(argv[1], "-h") == 0 || strcmp(argv[1], "--help") == 0)) {{
    print_usage();
    exit(0);
  }}

  // Determine the usage option based on argc
  if (argc == 1) {{
    option = 1; // Usage option 1: Process default parameter file "{project_name}.par"
  }} else if (argc == 2) {{
    // Check if the argument is a file
    FILE *file_check = fopen(argv[1], "r");
    if (file_check != NULL) {{
      fclose(file_check);
      option = 2; // Usage option 2: Process parameter file provided in argv[1]
    }} else if (argc == 1 + number_of_steerable_parameters) {{
      option = 3;
    }} else {{
      fprintf(stderr, "Error: Invalid number of arguments or file cannot be opened.\n");
      print_usage();
      exit(1);
    }}
  }} else if (argc == 1 + number_of_steerable_parameters) {{
    option = 3; // Usage option 3: Overwrite steerable parameters after processing "{project_name}.par"
  }} else if (argc == 2 + number_of_steerable_parameters) {{
    // Check if the first argument is a file
    FILE *file_check = fopen(argv[1], "r");
    if (file_check != NULL) {{
      fclose(file_check);
      option = 4; // Usage option 4: Overwrite steerable parameters after processing parameter file provided in argv[1]
    }} else {{
      fprintf(stderr, "Error: File cannot be opened for option 4.\n");
      print_usage();
      exit(1);
    }}
  }} else {{
    fprintf(stderr, "Error: Invalid number of arguments\n");
    print_usage();
    exit(1);
  }}

  // fprintf(stderr, "Using option %d\n", option);

  const char *filename = (option == 1 || option == 3) ? "{project_name}.par" : argv[1];
  FILE *file = fopen(filename, "r");
  if (file == NULL) {{
    print_usage();
    exit(1);
  }}
"""
    body += r"""
  char line[LINE_SIZE];
  char param[PARAM_SIZE];
  char value[PARAM_SIZE];
  int params_set[NUM_PARAMETERS] = {0}; // Record of parameters set (one for each parameter in the struct)

  while (fgets(line, sizeof(line), file)) {
    // Removing comments from the line
    char *comment_start = strchr(line, '#');
    if (comment_start != NULL) {
      *comment_start = '\0';
    }

    char *p = strtok(line, "=");
    if (p) {
      safe_copy(param, trim_space(p), sizeof(param));
      p = strtok(NULL, "=");
      if (p) {
        safe_copy(value, trim_space(p), sizeof(value));

        // Check for naming convention violations
        for (int i = 0; param[i]; i++) {
          if (!isalnum(param[i]) && param[i] != '_') {
            fprintf(stderr, "Error: Invalid parameter name %s.\n", param);
            exit(1);
          }
        }

        int param_index = -1;
        if (1 == 0) param_index = -2;
"""
    i = 0
    for key, CodeParam in par.glb_code_params_dict.items():
        if (
            CodeParam.add_to_parfile
            and CodeParam.commondata
            and (
                CodeParam.c_type_alias in ("int", "REAL")
                or "char" in CodeParam.c_type_alias
            )
        ):
            body += f'else if (strcmp(param, "{key}") == 0) param_index = {i};\n'
            i += 1
    body += r"""else fprintf(stderr, "Warning: Unrecognized parameter %s.\n", param);

        // Check for duplicates
        if (param_index != -1 && params_set[param_index] == 1) {
          fprintf(stderr, "Error: Duplicate parameter %s.\n", param);
          exit(1);
        }
        if (param_index != -1) params_set[param_index] = 1;

        // Assign values
        if (param_index == -2) exit(1); // impossible.
"""
    i = 0
    for key, CodeParam in par.glb_code_params_dict.items():
        if CodeParam.add_to_parfile and CodeParam.commondata:
            if CodeParam.c_type_alias == "int":
                body += f'else if(param_index == {i}) read_integer(value, &commondata->{key}, "{key}");\n'
                i += 1
            elif CodeParam.c_type_alias == "REAL":
                body += f'else if(param_index == {i}) read_double(value, &commondata->{key}, "{key}");\n'
                i += 1
            elif (
                "char" in CodeParam.c_type_alias
                and "[" in CodeParam.c_type_alias
                and "]" in CodeParam.c_type_alias
            ):
                CPsize = CodeParam.c_type_alias.split("[")[1].split("]")[0]
                body += f'else if(param_index == {i}) read_chararray(value, commondata->{key}, "{key}", {CPsize});\n'
                i += 1
    body += r"""        else {
          fprintf(stderr, "Error: Unrecognized parameter %s.\n", param);
          exit(1); // Exit on unrecognized parameter
        }
      }
    }
  }

  fclose(file);
  // Handling options 3 and 4: Overwriting steerable parameters
  if (option == 3 || option == 4) {
    // For options 3 and 4, we extract the last three arguments as steerable parameters
"""
    i = 0
    for key in cmdline_inputs:
        CodeParam = par.glb_code_params_dict[key]
        if CodeParam.add_to_parfile and CodeParam.commondata:
            if CodeParam.c_type_alias == "int":
                body += f'read_integer(argv[argc - number_of_steerable_parameters + {i}], &commondata->{key}, "{key}");\n'
                i += 1
            elif CodeParam.c_type_alias == "REAL":
                body += f'read_double(argv[argc - number_of_steerable_parameters + {i}], &commondata->{key}, "{key}");\n'
                i += 1
    body += "}\n"

    cfc.register_CFunction(
        includes=includes,
        prefunc=prefunc,
        desc=desc,
        c_type=c_type,
        name=name,
        params=params,
        body=body,
    )


def generate_default_parfile(project_dir: str, project_name: str) -> None:
    """
    Generates a default parameter file with sorted modules and parameters.

    :param project_dir: The parameter file will be stored in project_dir.

    >>> _, __ = par.register_CodeParameters("REAL", "CodeParameters_c_files", ["a", "pi_three_sigfigs"], [1, 3.14], commondata=True)
    >>> ___ = par.register_CodeParameter("#define", "CodeParameters_c_files", "b", 0)
    >>> _leaveitbe = par.register_CodeParameter("REAL", "CodeParameters_c_files", "leaveitbe", add_to_parfile=False, add_to_set_CodeParameters_h=False)
    >>> _leaveitoutofparfile = par.register_CodeParameter("REAL", "CodeParameters_c_files", "leaveitoutofparfile", add_to_parfile=False)
    >>> _str = par.register_CodeParameter("char", "CodeParameters_c_files", "string[100]", "cheese", commondata=True)
    >>> _bool = par.register_CodeParameter("bool", "CodeParameters_c_files", "BHaH_is_amazing", "true")
    >>> cfc.CFunction_dict.clear()
    >>> project_dir = Path("/tmp/tmp_BHaH_parfile")
    >>> project_dir.mkdir(parents=True, exist_ok=True)
    >>> generate_default_parfile(project_dir, "example_project")
    >>> print((project_dir / 'example_project.par').read_text())
    #### example_project BH@H parameter file. NOTE: only commondata CodeParameters appear here ###
    ###########################
    ###########################
    ### Module: CodeParameters_c_files
    a = 1                    # (type: REAL)
    pi_three_sigfigs = 3.14  # (type: REAL)
    string = "cheese"        # (type: char array)
    <BLANKLINE>
    """
    parfile_output_dict: Dict[str, List[str]] = defaultdict(list)

    # Sorting by module name
    for parname, CodeParam in sorted(
        par.glb_code_params_dict.items(), key=lambda x: x[1].module
    ):
        if CodeParam.commondata:
            CPtype = CodeParam.c_type_alias
            if CodeParam.add_to_set_CodeParameters_h and CodeParam.add_to_parfile:
                if CPtype == "char":
                    chararray_name = parname.split("[")[0]
                    parfile_output_dict[CodeParam.module].append(
                        f'{chararray_name} = "{CodeParam.defaultvalue}"  # (type: char array)\n'
                    )
                else:
                    parfile_output_dict[CodeParam.module].append(
                        f"{parname} = {CodeParam.defaultvalue}  # (type: {CPtype})\n"
                    )

    # Sorting the parameters within each module
    for module in parfile_output_dict:
        parfile_output_dict[module] = sorted(parfile_output_dict[module])

    output_str = f"#### {project_name} BH@H parameter file. NOTE: only commondata CodeParameters appear here ###\n"
    for module, params in sorted(parfile_output_dict.items()):
        output_str += "###########################\n"
        output_str += "###########################\n"
        output_str += f"### Module: {module}\n"
        output_str += "".join(params)

    def align_by_hash(original_string: str) -> str:
        lines = original_string.split("\n")
        max_length = max(
            line.find("#") for line in lines if "#" in line and line.strip()[0] != "#"
        )

        adjusted_lines = []
        for line in lines:
            if "#" in line and line.strip()[0] != "#":
                index = line.find("#")
                spaces_needed = max_length - index
                adjusted_line = line[:index] + " " * spaces_needed + line[index:]
                adjusted_lines.append(adjusted_line)
            else:
                adjusted_lines.append(line)

        return "\n".join(adjusted_lines)

    with (Path(project_dir) / f"{project_name}.par").open(
        "w", encoding="utf-8"
    ) as file:
        file.write(align_by_hash(output_str))


if __name__ == "__main__":
    import doctest
    import sys

    results = doctest.testmod()

    if results.failed > 0:
        print(f"Doctest failed: {results.failed} of {results.attempted} test(s)")
        sys.exit(1)
    else:
        print(f"Doctest passed: All {results.attempted} test(s) passed")
