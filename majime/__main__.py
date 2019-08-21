#!/usr/bin/env python
import sys, json, yaml, requests, random, io
import pkg_resources
from termcolor import colored
from urllib import parse

# This line is for pyinstaller and the binary release
##VERSION_PARSE##

if 'version' not in vars():
    version = pkg_resources.require("majime")[0].version

def getopts(argv):
    opts = {}
    while argv:
        if argv[0][0] == '-':
            try:
                opts[argv[0]] = argv[1]
            except:
                opts[argv[0]] = ""
        argv = argv[1:]
    return opts

def output(content, type=""):
    try:
        print(str(content))
    except:
        output("ERROR: output contains binary or UTF-8 content that this terminal cannot render.")

    sys.exit(0)

def exit_with_errror(message):
    print(colored(message, "red"))
    sys.exit(1)

def generate_test(url):

    print ("Generate test suite from " + str(url))
    try:
        swagger=requests.get(url).text
        data=json.loads(swagger)
        title = data["info"]["title"]
        host = data["host"]
        basepath = data["basePath"]
        scheme = data["schemes"][0]
    except:
        exit_with_errror("ERROR: cannot open or parse Swagger URL.")

    # print ("Title: " + str(title))
    print(colored("Title:", "yellow"), colored(title, "green"))
    # print ("Host: " + str(host))
    print(colored("Host:", "yellow"), colored(host, "green"))
    # print ("Base Path: " + str(basepath))
    print(colored("Base Path:", "yellow"), colored(basepath, "green"))
    # print ("Scheme: " + str(scheme))
    print(colored("Scheme:", "yellow"), colored(scheme, "green"))

    base_url = str(scheme) + "://" + str(host) + str(basepath)
    gen_file = str(title).replace(" ", "_") + "-" + str(random.randint(1000,9999)) + ".yaml"

    with io.open(gen_file, encoding='utf-8', mode='w') as f:
        f.write("Base: " + '"%s"' % base_url + "\n")
        f.write("Tests:\n")

        for api_path in data["paths"]:
            #print ("Path: " + api_path)
            print(colored("Path:", "yellow"), colored(api_path, "green"))
            for path_method in data["paths"][api_path]:
                method = str(path_method).upper()
                if method == "PARAMETERS":
                    continue
                try:
                    description = data["paths"][api_path][path_method]["description"]
                except:
                    description = ""

                try:
                    description += data["paths"][api_path][path_method]["summary"]
                except:
                    dummy=1

                try:
                    example = data["paths"][api_path][path_method]["parameters"][0]["schema"]["example"]
                except:
                    example = {}

                # We only want the first response
                try:
                    response = list(data["paths"][api_path][path_method]["responses"].keys())[0]
                except:
                    response = "200"
                try:
                    params = data["paths"][api_path][path_method]["parameters"]
                except:
                    params = ""

                if response == "default":
                    response = "200"

                query_parameters = []

                params_str = ""
                params_num = 0
                for p in params:
                    if str(p["in"]).upper() == "QUERY":
                        query_parameters.append(str(p["name"]))

                        if params_num == 0:
                            params_str += str(p["name"]) + "=XXX"
                        else:
                            params_str += "&" + str(p["name"]) + "=XXX"
                        params_num += 1

                # print ("\tMethod: " + method)
                print("\t" + colored("Method:", "magenta"), colored(method, "cyan"))
                # print ("\tDescription: " + description)
                print("\t" + colored("Description:", "magenta"), colored(description, "cyan"))
                # print ("\tQuery Parameters: " + str(query_parameters))
                print("\t" + colored("Query Parameters:", "magenta"), colored(query_parameters, "cyan"))
                # print ("\tExpected Response: " + str(response))
                print("\t" + colored("Expected Response:", "magenta"), colored(response, "cyan"))

                if params_str == "":
                    out_path = api_path
                else:
                    out_path = api_path + "?" + params_str

                if description == "":
                    f.write(' # %s\n' % method)
                else:
                    f.write(' # %s - %s\n' % (method, description))

                f.write(' - path: "%s"\n' % out_path)
                f.write('   method: "%s"\n' % method)

                f.write('   headers: ""\n')

                if method == "POST" or method == "PUT":
                    f.write('   content-type: "application/json"\n')
                    f.write('   body: %s\n' % str(example).replace("'", "\""))
                f.write('   expect-response: "%s"\n' % response)

                if method == "GET":
                    f.write('   expect-body: "json"\n')
                f.write('   \n')

    f.close()
    print(colored("\n%s created" % gen_file, "green"))

def perform_test(testfile, output_format, dryrun):

    try:
        with open(testfile, 'r') as stream:
            test_data = yaml.safe_load(stream)
    except:
        exit_with_errror("ERROR: cannot open or parse file")

    if dryrun == "yes":
        output(testfile + " successfully loaded.")
        
    majime_base = test_data["Base"]
    majime_host = majime_base.split("//")[-1].split("/")[0].split('?')[0]

    tests_run = 0
    tests_successful = 0
    tests_failed = 0
    json_out = {}
    json_out["tests"] = []
    json_out["output"] = {}

    for majime_test in test_data["Tests"]:
        majime_url = majime_base + majime_test["path"]
        majime_queryparams = dict(parse.parse_qsl(parse.urlsplit(majime_url).query))
        majime_baseurl = majime_url.split('?')[0].split('#')[0]
        majime_method = majime_test["method"]

        try:
            majime_ctype = majime_test["content-type"]
        except:
            majime_ctype = ""

        try:
            majime_payload1 = majime_test["body"]
            majime_payload = json.dumps(majime_payload1)

        except:
            majime_payload = ""

        majime_expect_response = majime_test["expect-response"]

        headers = { 'User-Agent': "majime-%s" % version}

        if majime_ctype != "":
            headers["Content-Type"] = majime_ctype

        try:
            response = requests.request(majime_method, majime_baseurl, data=majime_payload, params=majime_queryparams, headers=headers)
        except:
            print ("Fatal error when running test. Is the endpoint reachable?")
            sys.exit(1)

        code = response.status_code

        tests_run += 1

        if str(majime_expect_response) == str(code):
            tests_successful +=1
            json_out["tests"].append(dict(method=majime_method, url=majime_url, http_response=str(code), result="OK"))
        else:
            tests_failed +=1
            json_out["tests"].append(dict(method=majime_method, url=majime_url, http_response=str(code), http_expected_response=majime_expect_response, result="FAIL"))

    if tests_failed == 0:
        json_out["output"]["overall_result"] = "OK"
    else:
        json_out["output"]["overall_result"] = "FAIL"

    json_out["output"]["successful-tests"] = str(tests_successful)
    json_out["output"]["failed-tests"] = str(tests_failed)

    if output_format == "json":
        print(str(json_out).replace("'","\""))
    else:
        for t in json_out["tests"]:
            print("%s %s" % (t["method"], t["url"] ))
            if t["result"] == "OK":
                print (colored("HTTP " + str(t["http_response"]), "green" ))
            else:
                print (colored("HTTP " + str(t["http_response"]) + " but expected " + str(t["http_expected_response"]), "red" ))

        print("%s tests, %s successful and %s failed" % (tests_run, tests_successful, tests_failed))

    if tests_failed == 0:
        sys.exit(0)
    else:
        sys.exit(1)

def print_help():

    print ('''Majime - Dead Simple API Unit Tests

    Usage:

     -f Load and run tests from YAML file
        Example: majime -f test.yaml
     -g Generate test suite (YAML) from Swagger document
        Example: majime -g http://api.example.com/swagger.json

    Switches:

     -j JSON output for test runs
     -d Dry-Run, do not execute tests - good for testing your YAML file
    ''')

def main():
    args = getopts(sys.argv)
    if '-v' in args:
        output("Majime version " + str(version))
        sys.exit(0)

    if '-h' in args or args == {}:
        print_help()
        sys.exit(0)

    if '-j' in args:
        output_format = "json"
    else:
        output_format = "standard"

    if '-d' in args:
        dryrun = "yes"
    else:
        dryrun = "no"

    if '-g' in args:
        swagger_url = args['-g']
        generate_test(swagger_url)

    if '-f' in args:
        test_file = args['-f']
        perform_test(test_file, output_format, dryrun=dryrun)

if __name__ == '__main__':
    main()
