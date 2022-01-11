FROM hip:stage1

RUN pip install pybids siibra requests pyunicore

RUN pip install cmdstanpy && install_cmdstan
