
import os
import sys
import shutil
import yaml
import wget
import tarfile

WORKDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(os.getcwd(), ".packages")

def _split_filename(filename):
    (name, ext) = os.path.splitext(filename)
    (name1, ext1) = os.path.splitext(name)
    if ext1 == ".tar":
        return (name1, ext1+ext)
    return (name, ext)

def _load_yaml(filename):
    with open(filename) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return data

class PackageBuilder:
    def __init__(self, pack_name):
        self.workdir = WORKDIR
        self.outdir = OUTDIR
        self.desc_file = os.path.join(self.workdir, "packages", pack_name+".yaml")
        self.download_dir = os.path.join(self.workdir, "packages", ".download")
        self.prefix_root = os.path.join(self.outdir, "prefix_root")

    def build(self):
        self.pack_desc = _load_yaml(self.desc_file)
        # print(self.pack_desc)
        self._download_archive()
        self._extract_archive()
        self._build_package()

    def _download_archive(self):
        # print("download package ...")
        url = self.pack_desc["archive"]["remote"]
        filename = self.pack_desc["archive"]["local"]
        self.archive = os.path.join(self.download_dir, filename)
        print("download %s to %s" % (url, self.archive))
        if not os.path.exists(self.archive):
            if not os.path.isdir(self.download_dir):
                os.makedirs(self.download_dir)
            wget.download(url, self.archive)

    def _extract_archive(self):
        filename = self.pack_desc["archive"]["local"]
        (name, ext) = _split_filename(filename)
        self.build_dir = os.path.join(self.prefix_root, "usr", "src", name)
        print("extract %s to %s" % (self.archive, self.build_dir))
        if ext in [".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tbz2", ".tar.xz", ".txz"]:
            shutil.rmtree(self.build_dir, ignore_errors=True)
            src_parent_dir = os.path.dirname(self.build_dir)
            with tarfile.open(self.archive, "r") as tar:
                tar.extractall(src_parent_dir)

    def _build_package(self):
        build_type = self.pack_desc["build"]["type"]
        if build_type == "cmake":
            self._build_for_cmake()

    def _build_for_cmake(self):
        cmake_dir = os.path.join(self.build_dir, "build-cmake-bpp")
        if not os.path.isdir(cmake_dir):
            os.makedirs(cmake_dir)
        cmd = \
            "cd %s && PREFIX_ROOT='%s' && cmake -DCMAKE_INSTALL_PREFIX='%s' .. && make && make install" \
            % (cmake_dir, self.prefix_root, self.prefix_root)
        print("build command: %s" % cmd)
        print("--------------------")
        os.system(cmd)

def dump_usage():
    print('python bpp.py <command>')
    print('   pack <package_name>           构建单个包')

def main():
    print("build packages")
    print("workdir: %s" % WORKDIR)
    print("output: %s" % OUTDIR)

    if len(sys.argv) < 2:
        dump_usage()
        return

    if sys.argv[1] == "pack":
        builder = PackageBuilder(sys.argv[2])
        builder.build()

if __name__ == "__main__":
    main()

