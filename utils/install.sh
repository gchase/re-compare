# This assumes current directory is the re-compare repository root

# RE2-DEPENDINCIES
pip3 install matplotlib numpy pandas ply tqdm pytest cython pytest-mock mocker &&
sudo apt install python3-tk gnuplot &&

# BASELINE ALGORITHM DEPENDINCIES
# install re2
git clone https://code.googlesource.com/re2 &&
cd re2 &&
make &&
sudo make install &&
cd .. &&
rm -rf re2 &&

pip3 install https://github.com/andreasvc/pyre2/archive/master.zip &&


#install modified grep
wget http://ftp.gnu.org/gnu/grep/grep-3.1.tar.xz &&
tar xf grep-3.1.tar.xz &&
cp utils/grep.c grep-3.1/src &&
cd grep-3.1 &&
./configure --bindir=$(pwd) &&
make &&
sudo make install &&
cp ./grep ../re_compare/algorithms/modified_grep &&
cd .. &&
rm -rf grep-3.1 

