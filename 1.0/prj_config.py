config=
{
    # Project description
    "desc"             : "",
    "version"          : "1.0.0.Alpha",
    "maintainer"       : "",
    "maintainer_url"   : "",
    "maintainer_email" : "",
    "dir"              : "",
    "lic"              : "mit",
    "team"             : 
        {
            "manager"     : 
                {
                    "name"  : "",
                    "email" : ""
                },
            "developers"  : [
                {
                    "name"  : "",
                    "email" : ""
                },
            ],
            "testers"     : [
                {
                    "name"  : "",
                    "email" : ""
                },
            ],
            "designers"   : [
                {
                    "name"  : "",
                    "email" : ""
                },
            ],
        }

    # Project dependencies to download
    "dependencies"   :  {
                            "git":  [],
                            "svn":  [],
                            "wget": []
                        },

    # Project options
    "type"           : "lib", # May be cli/lib/qtapp
    "tabstop"        : 4,
    "git_repo"       : "",
    "test_dir"       : "tests",
    "snake_case"     : True,

    # Compiler options
    "builds"         :
    {
        "common":
        {
            "cxx"           : "g++",
            "cc"            : "gcc",
            "cxx_flags"     : "-O2 -Wall -pedantic -std=c++14",
            "inc_dirs"      : "include",
        },
        "qmake"          :
        {
            "linux32.static" : "qmake",
            "linux32.shared" : "qmake",
            "linux64.static" : "qmake",
            "linux64.shared" : "qmake",
            "win32.static"   : "qmake",
            "win32.shared"   : "qmake",
            "win64.static"   : "qmake",
            "win64.shared"   : "qmake"
        },
        "linux32.static" : {
            "cross_compile" : "",
            "arch"          : "i686",
            "linker_flags"  : "-static",
            "lib_dirs"      : "",
            "out_dir"       : ""
        },
        "linux32.shared" : {
            "cross_compile" : "",
            "arch"          : "i686",
            "linker_flags"  : "-static-libgcc -static-libstdc++",
            "lib_dirs"      : "",
            "out_dir"       : ""
        },
        "linux64.static" : {
            "cross_compile" : "x86_64-linux-gnu-",
            "arch"          : "x86_64",
            "linker_flags"  : "-static",
            "lib_dirs"      : "",
            "out_dir"       : ""
        },
        "linux64.shared" : {
            "cross_compile" : "x86_64-linux-gnu-",
            "arch"          : "x86_64",
            "linker_flags"  : "-static-libgcc -static-libstdc++",
            "lib_dirs"      : "",
            "out_dir"       : ""
        },
        "win32.static" : {
            "cross_compile" : "i686-w64-mingw32-",
            "arch"          : "i686",
            "linker_flags"  : "-static",
            "lib_dirs"      : "",
            "out_dir"       : ""
        },
        "win32.shared" : {
            "cross_compile" : "i686-w64-mingw32-",
            "arch"          : "i686",
            "linker_flags"  : "-static-libgcc -static-libstdc++",
            "lib_dirs"      : "",
            "out_dir"       : ""
        },
        "win64.static" : {
            "cross_compile" : "x86_64-w64-mingw32-",
            "arch"          : "x86_64",
            "linker_flags"  : "-static",
            "lib_dirs"      : "",
            "out_dir"       : ""
        },
        "win64.shared" : {
            "cross_compile" : "x86_64-w64-mingw32-",
            "arch"          : "x86_64",
            "linker_flags"  : "-static-libgcc -static-libstdc++",
            "lib_dirs"      : "",
            "out_dir"       : ""
        },
    }
}
