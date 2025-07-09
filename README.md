# How to Run Prometheus Using Lepton Injector & Earth Model Svc

## Setting up the environment

First we need a consistent conda environment for the installation that follows

### STEP O: Install pre-req \& Download Anaconda

#### Made for Ubuntu environment

Please follow instructions from: [Anaconda3 Installation for Linux](https://www.anaconda.com/docs/getting-started/anaconda/install#macos-linux-installation:navigator-dependencies)

Be advised that the download is around 1 Gig

```bash=

sudo apt install libgl1-mesa-glx libegl1-mesa libxrandr2 libxrandr2 libxss1 libxcursor1 libxcomposite1 libasound2 libxi6 libxtst6
wget https://repo.anaconda.com/archive/Anaconda3-2025.06-0-Linux-x86_64.sh
bash Anaconda3-2025.06-0-Linux-x86_64.sh
# To refresh paths installed by Anaconda
source ~/.bashrc
```

Main course post conda installation:

```bash=
conda create --name prom_env -c conda-forge python=3.11
conda activate prom_env
conda install -c conda-forge boost boost-cpp h5py matplotlib photospline suitesparse cfitsio cmake ipykernel jupyter
python3 -m pip install proposal
```
Up next, time to download & install the packages

## Lepton Injector

### Installing LeptonInjector

```bash=
cd ~
mkdir lepinj
cd lepinj
git clone https://github.com/icecube/LeptonInjector.git
mv LeptonInjector source
cd source
git checkout b5ab876
```

Now we must be careful to compile with the proper `CMakeLists.txt` file inside
`~/lepinj/source`

Use the `CMakeLists.txt` provided with this github repo; the default **LeptonInjector** doesn't compile `EarthModelService`

```bash=
cd ~/lepinj/source/
rm -rf CMakeLists.txt
git clone https://github.com/jirahandler/prometheus-hacks ~/prometheus-hacks
cp ~/prometheus-hacks/CMakeLists.txt .
cd ..
#The step above is used to fix the CMake file for proper shared object compilation
mkdir build install
```

In the same conda environment, issue these commands:

```bash=
cd ~/lepinj/build
export CONDA_PREFIX=/home/$USER/anaconda3/envs/prom_env
$CONDA_PREFIX/bin/cmake \
  -DCMAKE_INSTALL_PREFIX=$CONDA_PREFIX \
  -DCMAKE_PREFIX_PATH=$CONDA_PREFIX    \
  -DCMAKE_POLICY_DEFAULT_CMP0074=NEW   \
  -DCMAKE_POLICY_DEFAULT_CMP0167=NEW   \
  -DCMAKE_POLICY_VERSION_MINIMUM=4.0  \
  -DPython_ROOT_DIR=$CONDA_PREFIX      \
  ../source
make -j$nproc && make install
```
Don't do sudo make install; not needed because it installas stuff into system bin path.

## Installing Prometheus

```bash=
cd ~
git clone https://github.com/Harvard-Neutrino/prometheus.git
cd prometheus
git checkout e072a5f
python3 -m pip install -e .
```
We need to make some edits inside the prometheus package. It needs a line replacement.

```bash=
cd ~/prometheus/prometheus/injection
vim lepton_injector_utils.py

```
Matching the function definitions, please make a single line edit as below

```bash=
earth_model_dir = "/".join(path_dict["earth model location"].split("/")[:-2]) + "/"
    earth_model_name = path_dict["earth model location"].split("/")[-1].split(".")[0]
    earth = em.EarthModelService(
        "Zorg",
        earth_model_dir,
        [earth_model_name],
        ["Standard"],
        "NoIce",
        0.0,
        -detector_offset[2]
    )
    # Replace
    # controller.SetEarthModelService(earth)
    # by the uncommented line below
    controller.SetEarthModel("Zorg", earth_model_dir)
    # Other stuff in your script as usual.
```
Then, do the following:

Install it again after edits on the same terminal session as below.
Also needs to be installed on every new shell you're working with and on every subsequent change(s) in the same active shell

```bash=
cd ~/prometheus/
python3 -m pip install -e .
```

Time to check the  PREM cards.

```bash=
cd ~/prometheus/resources/earthparams/densities/
ls PREM_mmc.dat
# IF PREM_mmc.dat doesn't show up, do, to have a PREM card to run (for example)
cp PREM_south_pole.dat PREM_mmc.dat
```
Next, go to the `examples` directory inside `~/prometheus` to run the sim.
First you gotta copy over the revamped simulation test script from this repo (see in the bash code below).

Ensure that your `conda environment` is active.

```bash=
cd ~/prometheus/examples/
cp ~/prometheus-hacks/test-sim.py .
python3 test-sim.py
 ```
The sim may take about 10 minutes with 100 events on less powerful machines and will create some tables.

This will create a folder called `output` in `~/prometheus/examples/` with `h5 & parquet` files on successful run.

Remember, Prometheus package must be installed in each terminal `tty` session that you're working on.









