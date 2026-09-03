import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
from conan.tools.files import copy, download, get, rmdir

required_conan_version = ">=2.1"


class KUMIConan(ConanFile):
    name = "kumi"
    description = "C++20 tuple and tuple-based algorithms library."
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://jfalcou.github.io/kumi/"
    topics = ("kumi", "tuple", "c++", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def requirements(self):
        self.tool_requires("copacabana/7.0")

    def validate(self):
        check_min_cppstd(self, 20)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # This release downloads CPM at configure time; seeding the cache keeps the
        # configure step off the network.
        cpm = self.conan_data["sources"]["cpm"]
        download(self, cpm["url"], os.path.join(self.source_folder, "cpm-cache", "cpm", cpm["filename"]),
                 sha256=cpm["sha256"])

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CPM_SOURCE_CACHE"] = os.path.join(self.source_folder, "cpm-cache")
        # The build is written with copacabana, which CPM fetches at configure time; the
        # package installed here is handed to CPM instead.
        tc.cache_variables["CPM_COPACABANA_SOURCE"] = os.path.join(
            self.dependencies.build["copacabana"].package_folder, "res")
        tc.cache_variables["CPM_LOCAL_PACKAGES_ONLY"] = True
        tc.cache_variables["KUMI_BUILD_TEST"] = False
        tc.cache_variables["KUMI_BUILD_DOCUMENTATION"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()

    def package(self):
        copy(self, "LICENSE.md", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
