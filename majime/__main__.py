#!/usr/bin/env python
import sys, json, yaml, requests, random
import pkg_resources
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
    print(message)
    sys.exit(1)

def gen_test(url):

    print ("Trying to generate test suite from " + str(url))
    try:
        swagger=requests.get(url).text
        data=json.loads(swagger)
        title = data["info"]["title"]
        host = data["host"]
        basepath = data["basePath"]
        scheme = data["schemes"][0]
    except:
        exit_with_errror("ERROR: cannot open or parse Swagger URL.")

    print ("Title: " + str(title))
    print ("Host: " + str(host))
    print ("Base Path: " + str(basepath))
    print ("Scheme: " + str(scheme))

    for api_path in data["paths"]:
        print ("Path: " + api_path)
        for path_method in data["paths"][api_path]:
            method = str(path_method).upper()
            description = data["paths"][api_path][path_method]["description"]

            # We only want the first response
            response = list(data["paths"][api_path][path_method]["responses"].keys())[0]
            params = data["paths"][api_path][path_method]["parameters"]
            query_parameters = []

            for p in params:
                if str(p["in"]).upper() == "QUERY":
                    query_parameters.append(str(p["name"]))

            print ("\tMethod: " + method)
            print ("\tDescription: " + description)
            print ("\tQuery Parameters: " + str(query_parameters))
            print ("\tExpected Response: " + str(response))


    o = """Title: %s
    Host: %s
    Base Path: %s
    Scheme: %s
    """ % (title, host, basepath, scheme)

    print(random.randint(1000,9999))
    #with io.open('test.html', encoding='utf-8', mode='w') as f:
    #f.write(stuff)
    #f.close()


def main():
    args = getopts(sys.argv)
    if '-v' in args:
        output("Majime version " + str(version))
        sys.exit(0)

    if '-gen' in args:
        swagger_url = args['-gen']

        gen_test(swagger_url)


if __name__ == '__main__':
    main()
