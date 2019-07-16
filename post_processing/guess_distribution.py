import json
import os

# from scipy.stats import alpha, betaprime, wald, lognorm
import scipy.stats as st
# from skgof import ks_test, cvm_test, ad_test
import logging
import argparse
import numpy as np
# Adds a very verbose level of logs
import collections
import random
import math
import time


################################################################################
#                                                                              #
#                            Answere stack overflow                            #
#                                                                              #
################################################################################
# https://stackoverflow.com/questions/6620471/fitting-empirical-distribution-to-theoretical-ones-with-scipy-python

import warnings
# import numpy as np
# import pandas as pd
# import scipy.stats as st
# import statsmodels as sm
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams['figure.figsize'] = (16.0, 12.0)
plt.style.use('seaborn-deep')

DEBUG_LEVELV_NUM = 9
logging.addLevelName(DEBUG_LEVELV_NUM, "DEBUGV")

def debugv(self, message, *args, **kws):
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(DEBUG_LEVELV_NUM):
        self._log(DEBUG_LEVELV_NUM, message, args, **kws)


logging.Logger.debugv = debugv
log = logging.getLogger("post-processing")

# global variable
# data = []


# Tries to apply colors to logs
def applyColorsToLogs():
    try:
        import coloredlogs

        style = coloredlogs.DEFAULT_LEVEL_STYLES
        style['debugv'] = {'color': 'magenta'}
        coloredlogs.install(
            show_hostname=False, show_name=True,
            logger=log,
            level=DEBUG_LEVELV_NUM,
            fmt='%(asctime)s [%(levelname)8s] %(message)s'
            # Default format:
            # fmt='%(asctime)s %(hostname)s %(name)s[%(process)d] %(levelname)s
            #  %(message)s'
        )
    except ImportError:
        print("Can't import coloredlogs, logs may not appear correctly.")
        # log.error("Can't import coloredlogs, logs may not appear correctly.")


def logSetup(level):
    # if -vv option as program argument
    if level == 2:
        log.setLevel(DEBUG_LEVELV_NUM)
        log.info("Debug is Very Verbose.")
    # if -v option as program argument
    elif level == 1:
        log.setLevel(logging.DEBUG)
        log.info("Debug is Verbose.")
    # if no (-v) option
    elif level == 0:
        log.setLevel(logging.INFO)
        log.info("Debug is Normal.")
    else:
        # else
        log.setLevel(logging.INFO)
        log.warning("Logging level \"{}\" not defined, setting \"normal\" instead"
                    .format(level))


applyColorsToLogs()


def file2list(file_path, separator):
    with open(file_path) as f:
        content = f.readlines()
        return [x.strip().split(separator) for x in content]


def json_convert(jsonpath_expr, json_dir):
    try:
        files = [f for f in os.listdir(json_dir) if os.path.isfile(os.path.join(json_dir, f)) and f.endswith(".json")]
    except Exception:
        raise Exception("Cannot open dir")

    # Process each file into the rows
    numFiles = len(files)
    log.info("Processing " + str(numFiles) + " files")

    data = []
    # global data

    for filename in files:

        log.debugv("$ Processing file number " + str(numFiles) + ": " + filename + " JSON file")
        numFiles -= 1

        with open(json_dir + "/" + filename) as f:
            mwjson = json.load(f)

        name = filename.split('.')[0]

        # log.debug("my name is: " + str(name))
        parse = jsonpath_expr.split('.')
        # log.debug("jsonpath parsed in: " + str(parse))

        # PATCH: use variable type the next time
        data.append(
            {'name': name,
             'value': int(mwjson[name][parse[2]][parse[3]])
             })
        # data.append(int(mwjson[name][parse[2]][parse[3]]))

    log.debug("JSON first 10 values: " + str(data[:10]))
    log.debug("This list has " + str(len(data)) + " elements")
    return data


def androzoo2data(az_list_path, separator):
    data = []

    az_list = file2list(az_list_path, separator)

    for line in az_list:
        d = {
            'name': line[0],
            'size': int(line[1]),
            'year': line[2]
             }
        data.append(d)

    log.debug("Androzoo first 10 values: " + str(data[:10]))
    log.debug("This list has " + str(len(data)) + " elements")

    return data


# Create models from data
def best_fit_distribution(data, bins=None, ax=None, kde=False):
    """Model data by finding best fit distribution to data"""
    # Get histogram of original data
    if bins is None:
        max_exp = int(math.floor(math.log(max(data), 10)))
        binwidth = 10**(max_exp - 3)
        bins = np.arange(min(data), max(data) + binwidth, binwidth)
    y, x = np.histogram(data, bins=bins, density=True)
    x = (x + np.roll(x, -1))[:-1] / 2.0

    # Distributions to check
    DISTRIBUTIONS = [
        st.alpha,st.anglit,st.arcsine,st.beta,st.betaprime,st.bradford,st.burr,st.cauchy,st.chi,st.chi2,st.cosine,
        st.dgamma,st.dweibull,st.erlang,st.expon,st.exponnorm,st.exponweib,st.exponpow,st.f,st.fatiguelife,st.fisk,
        st.foldcauchy,st.foldnorm,st.frechet_r,st.frechet_l,st.genlogistic,st.genpareto,st.gennorm,st.genexpon,
        st.genextreme,st.gausshyper,st.gamma,st.gengamma,st.genhalflogistic,st.gilbrat,st.gompertz,st.gumbel_r,
        st.gumbel_l,st.halfcauchy,st.halflogistic,st.halfnorm,st.halfgennorm,st.hypsecant,st.invgamma,st.invgauss,
        st.invweibull,st.johnsonsb,st.johnsonsu,st.ksone,st.kstwobign,st.laplace,st.levy,st.levy_l,# st.levy_stable,
        st.logistic,st.loggamma,st.loglaplace,st.lognorm,st.lomax,st.maxwell,st.mielke,st.nakagami,st.ncx2,st.ncf,
        st.nct,st.norm,st.pareto,st.pearson3,st.powerlaw,st.powerlognorm,st.powernorm,st.rdist,st.reciprocal,
        st.rayleigh,st.rice,st.recipinvgauss,st.semicircular,st.t,st.triang,st.truncexpon,st.truncnorm,st.tukeylambda,
        st.uniform,st.vonmises,st.vonmises_line,st.wald,st.weibull_min,st.weibull_max,st.wrapcauchy
    ]

    # Best holders
    best_distribution = st.norm
    best_params = (0.0, 1.0)
    best_sse = np.inf

    # distribution = st.gaussian_kde(data, 0.07)

    # pdf = distribution.pdf(x)
    # sse = np.sum(np.power(y - pdf, 2.0))

    # # if axis pass in add to plot
    # try:
    #     if ax:
    #         # pd.Series(pdf, x).plot(ax=ax)
    #         print("Here I should add the PDF curve to the plot")
    # # end
    # except Exception:
    #     pass

    # # identify if this distribution is better
    # if best_sse > sse > 0:
    #     best_distribution = distribution
    #     best_sse = sse
    #     log.info("Best so far: kernel density estimation (SSE: " + str(sse) + ")")

    # Estimate distribution parameters from data
    for distribution in DISTRIBUTIONS:
        log.info("Evaluating " + str(distribution.name))
        # Try to fit the distribution
        try:
            # Ignore warnings from data that can't be fit
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')

                # fit dist to data
                params = distribution.fit(data)

                # Separate parts of parameters
                arg = params[:-2]
                loc = params[-2]
                scale = params[-1]

                # Calculate fitted PDF and error with fit in distribution
                pdf = distribution.pdf(x, loc=loc, scale=scale, *arg)
                sse = np.sum(np.power(y - pdf, 2.0))

                # if axis pass in add to plot
                try:
                    if ax:
                        # pd.Series(pdf, x).plot(ax=ax)
                        print("Here I should add the PDF curbe to the plot")
                # end
                except Exception:
                    pass

                # identify if this distribution is better
                if best_sse > sse > 0:
                    best_distribution = distribution
                    best_params = params
                    best_sse = sse
                    log.info("Best so far: "+str(best_distribution.name) + " (SSE: " + str(sse) + "), with: " + str(best_params))

        except Exception:
            print("An exception occurred with " + str(distribution.name))
            pass

    log.info("That's all folks!")

    time.sleep(30)

    return best_distribution, best_params
    # return best_distribution.name, best_params


# def make_pdf(dist, params, size=10000):
#     """Generate distributions's Probability Distribution Function """
#
#     # Separate parts of parameters
#     arg = params[:-2]
#     loc = params[-2]
#     scale = params[-1]
#
#     # Get sane start and end points of distribution
#     start = dist.ppf(0.01, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.01, loc=loc, scale=scale)
#     end = dist.ppf(0.99, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.99, loc=loc, scale=scale)
#
#     # Build PDF and turn into pandas Series
#     x = np.linspace(start, end, size)
#     y = dist.pdf(x, loc=loc, scale=scale, *arg)
#     pdf = pd.Series(y, x)
#
#     return pdf

# print(ks_test((1, 2, 3), uniform(0, 4)))
# # GofResult(statistic=0.25, pvalue=0.97...)
#
# print(cvm_test((1, 2, 3), uniform(0, 4)))
# # GofResult(statistic=0.04..., pvalue=0.95...)
#
# data = norm(0, 1).rvs(random_state=1, size=100)
# print(ad_test(data, norm(0, 1)))
# # GofResult(statistic=0.75..., pvalue=0.51...)

# print(ad_test(data, norm(.3, 1)))
# # GofResult(statistic=3.52..., pvalue=0.01...)

# test_pvalue = ks_test((.4, .1, .7), uniform(0, 1)).pvalue
# print("test p-value is: " + str(test_pvalue))
# if ks_test((.4, .1, .7), uniform(0, 1)).pvalue < .05:
#     print("Hypothesis rejected with 5% significance.")


def guess_my_distribution(data):
    # data = json_convert(jsonpath_expr, json_dir)

    best_fit_name, best_fit_params = best_fit_distribution(data)
    print("Best distritibution: " + str(best_fit_name) + ", with the following parameters: " + str(best_fit_params))
    # best_dist = getattr(st, best_fit_name)


def buckets(discrete_set, amin=None, amax=None, bucket_size=None):
    if amin is None: amin=min(discrete_set)
    if amax is None: amax=min(discrete_set)
    if bucket_size is None: bucket_size = (amax-amin)/20

    def to_bucket(sample):
        if not (amin <= sample <= amax): return None  # no bucket fits
        return int((sample - amin) // bucket_size)
    b = collections.Counter(to_bucket(s)
            for s in discrete_set if to_bucket(s) is not None)
    return amin, amax, bucket_size, b


def makesample(N, buckelems, mi, ma, bs, dist):
    s = []
    for _ in range(N):
        buck = random.choice(buckelems)
        # x = random.uniform(mi+buck*bs, mi+(buck+1)*bs)
        x = dist.rvs(mi+buck*bs, mi+(buck+1)*bs)
        s.append(x)
    return s


def dist_generator(dist, n):
    yield from dist.rvs(n)


def kde_sample_generator(kde):
    resample = kde.resample()[0]
    # print("this is a resample of size: " + str(len(resample)))
    for sample in resample:
        # print("This sample is :" + str(sample))
        yield sample


def create_list_by_dist(data, androzoo, dist=None, use_kde=False, kde_bandwidth=0.1):
    # data = from jsons
    # androzoo = from androzoo_file

    data_values = [x['value'] for x in data]

    # mi, ma, bs, bks = buckets(discrete_set)
    # mi, ma, bs, bks = buckets(data)
    # buckelems = list(bks.elements())
    # N = len(data)
    # return makesample(N, buckelems, mi, ma, bs, dist)

    # Guess the distribution of MWlist, get the name and parameters of the distribution
    if dist is None and use_kde is False:
        binwidth = 10**5
        bins = np.arange(0, max(data_values) + binwidth, 2*binwidth)
        dist, dist_params = best_fit_distribution(data_values, bins=bins)

        arg = dist_params[:-2]
        loc = dist_params[-2]
        scale = dist_params[-1]

        # log.debug("Creating a similar distribution with " + str(n) + " values")
        # Create a random list following MWlist (guessing it: ntc, gengamma, fisk, johnsonsu ...)
        guessed_dist = dist(loc=loc, scale=scale, *arg)
    elif dist is not None:
        guessed_dist = dist

    n = len(androzoo)

    log.debug("Creating a similar distribution with " + str(n) + " values")
    # try:
    #     # guessed_values = guessed_dist.rvs(n)
    #     guessed_values = dist_generator(dist, n)
    # except ValueError:
    #     log.warning("The value for this is " + str(guessed_dist))
    #     quit()

    new_data = []

    years = {
        '2015': 0,
        '2016': 0,
        '2017': 0,
        '2018': 0,
    }

    # elements that where not taken into account, they will be reused when androzoo is exhausted
    # relist_androzoo = []

    # n = len(GWlist)
    # for num in range(n):
    # for num in range(n):
    #     log.debug("Processing GW num: " + str(num))
    #     # Get random element dist_elem from dist
    #     # rand_dist = np.random(dist(dist_params).rvs(n))
    #     # rand_dist = np.random.choice(guessed_values)
    #     rand_from_guesses = next(guessed_values)
        # for element in GWlist:

    # rand_from_guesses = next(guessed_values)

    if use_kde is True:
        kde = st.gaussian_kde(data_values, kde_bandwidth)
        sample = kde_sample_generator(kde)

    kde_exausted = False

    rand_from_guesses = 0

    while rand_from_guesses <= 0:
        if use_kde is True:
            rand_from_guesses = next(sample)
            # log.info("rand len: " + str(len(rand_from_guesses)))
        else:
            rand_from_guesses = dist.rvs()

    orig_androzoo = androzoo

    while len(new_data) < 5000:
        relist_androzoo = []
        # rand_from_guesses = next(guessed_values)
        log.debug("Processing GW num: " + str(len(new_data)))
        log.debug("Guessed value: " + str(rand_from_guesses))
        # index = -1
        for index, element in enumerate(androzoo):
            # rand_from_guesses = next(guessed_values)
            # if element is similar to dist_elem:
            # TODO: parametrize the porcentage
            # if element in new_data:
            #     log.debug("This element is already in new_data, continue")
            #     _, *androzoo = androzoo
            #     log.debug("androzoo now has " + str(len(androzoo)) + " elements")
            #     continue

            if element['size'] < rand_from_guesses*1.05 and element['size'] > rand_from_guesses*0.95:
                # Put in dist_GWlist
                log.debug(str(index) + " element " + str(element) + " added")
                if len(new_data) < 5000:
                    try:
                        if years[element['year']] < 5000/4:
                            years[element['year']] += 1
                            new_data.append(element)
                            rand_from_guesses = 0
                            while rand_from_guesses <= 0:
                                if use_kde is True:
                                    try:
                                        rand_from_guesses = next(sample)
                                    except StopIteration:
                                        kde_exausted = True
                                        break
                                else:
                                    rand_from_guesses = dist.rvs()
                            # while rand_from_guesses <= 0:
                            #     rand_from_guesses = guessed_dist.rvs()
                    except KeyError:
                        continue
                else:
                    break
                # rand_from_guesses = next(guessed_values)
                # _, *androzoo = androzoo
            else:
                # log.debug(str(index) + " This element doesn't follow, saving it")
                relist_androzoo.append(element)
                # Pop element from GWlist
                # my_index = androzoo.index(element)
                # androzoo.pop(my_index)
                # (?) Pop element from dist
            # if len(new_data) >= 5000:
            #     break
        log.debug("androzoo exhausted, changing")
        # log.info("Processing GW num: " + str(len(new_data)))
        # log.info("By year, 2015: " + str(years['2015']) + " 2016: " + str(years['2016']) +
        #          " 2017: " + str(years['2017']) + " 2018:" + str(years['2018']))
        rand_from_guesses = 0
        while rand_from_guesses <= 0:
            if use_kde is True:
                try:
                    rand_from_guesses = next(sample)
                except StopIteration:
                    kde_exausted = True
                    break
            else:
                rand_from_guesses = dist.rvs()

        if len(androzoo) != len(relist_androzoo) and kde_exausted is False:
            androzoo = relist_androzoo
        elif kde_exausted is True:
            kde = st.gaussian_kde(data_values, kde_bandwidth)
            sample = kde_sample_generator(kde)
            log.info("Processing GW num: " + str(len(new_data)))
            log.info("2015: " + str(years['2015']))
            log.info("2016: " + str(years['2016']))
            log.info("2017: " + str(years['2017']))
            log.info("2018: " + str(years['2018']))
            log.info("No other apks to try, reseting")
            new_data = []
            androzoo = orig_androzoo
            years = {
                '2015': 0,
                '2016': 0,
                '2017': 0,
                '2018': 0,
            }
            if use_kde is True:
                kde = st.gaussian_kde(data_values, kde_bandwidth)
                sample = kde_sample_generator(kde)
            kde_exausted = False
            time.sleep(1)
        else:
            # log.info("No other apks to try, exiting")
            # break
            log.info("Processing GW num: " + str(len(new_data)))
            log.info("2015: " + str(years['2015']))
            log.info("2016: " + str(years['2016']))
            log.info("2017: " + str(years['2017']))
            log.info("2018: " + str(years['2018']))
            log.info("No other apks to try, reseting")
            new_data = []
            androzoo = orig_androzoo
            years = {
                '2015': 0,
                '2016': 0,
                '2017': 0,
                '2018': 0,
            }
            if use_kde is True:
                kde = st.gaussian_kde(data_values, kde_bandwidth)
                sample = kde_sample_generator(kde)
            kde_exausted = False
            time.sleep(1)

    log.info("Processing GW num: " + str(len(new_data)))
    log.info("By year, 2015: " + str(years['2015']) + " 2016: " + str(years['2016']) +
             " 2017: " + str(years['2017']) + " 2018:" + str(years['2018']))

    return new_data


if __name__ == '__main__':
    data = []
    parser = argparse.ArgumentParser(description="Guess the distribution of a series of data")
    parser.add_argument("jsonpath_expr", help="JSONPath expression to search the data")
    parser.add_argument("json_dir", help="JSON files directory (full path)")
    parser.add_argument("output_file", help="Name of output file")
    parser.add_argument('-v', help='Output information to the standart output (-vv is very verbose)', action="count")
    parser.add_argument("--androzoo_file", help="Androzoo file (separated by comma)")

    args = parser.parse_args()

    if args.v is None:
        logSetup(0)
    else:
        logSetup(args.v)

    # guess_distribution(args.jsonpath_expr, args.json_dir)
    # guess_my_distribution(args.jsonpath_expr, args.json_dir)
    log.debug("The arguments are: " + str(args))

    # quit()

    # json_convert retuns a list
    data = json_convert(args.jsonpath_expr, args.json_dir)
    log.info("JSON data processed")

    # androzoo2data returns a list
    androzoo = androzoo2data(args.androzoo_file, ',')
    log.info("Androzoo file data processed")

    # TODO: parameterize in program argument: distribution name and parameters

    # params = (0.352741247536232, 1752521.9999999618, 163469.98334998888)
    # params = (0.352741247536232, 1752521.9999999618, 163469.98334998888)
    # arg = params[:-2]
    # loc = params[-2]
    # scale = params[-1]

    # my_dist = st.gennorm(loc=loc, scale=scale, *arg)
    # res_data = create_list_by_dist(data, androzoo, my_dist)

    # res_data = create_list_by_dist(data, androzoo)

    res_data = create_list_by_dist(data, androzoo, use_kde=True, kde_bandwidth=0.05)

    print("res_data size: " + str(len(res_data)))

    # with open('res4.txt', 'w') as f:
    with open(args.output_file, 'w') as f:
        for item in res_data:
            f.write("{},{:d},{}\n".format(item['name'], item['size'], item['year']))

    # res_data = create_list_by_dist(data, androzoo)
    print(len(res_data))

# ------------------------------------------

# create_list_by_dist
# input: list of MW, jsonpath expression,
# output: list = [{'nom_apk','size'}]

# ==========================================

# Discretize list of MW by groups of 10k bytes
# Guess distribution of listMW_disc (by 10k bytes)
# For each element in the GWLIST:
    # Get the discrete grouping of the element
    # If the grouping of the element is not full in new_GWLIST:
        # Get the element
        # new_GWLIST.new.group[element.group] += 1
# Print dist

# ==========================================

# Guess the distribution of MWlist, get the name and parameters of the distribution
# Create a random list following MWlist (guessing it: ntc, gengamma, fisk, johnsonsu ...)
# n = len(GWlist)
# for num in range(n):
    # Get random element dist_elem from dist
    # for element in GWlist:
        # if element is similar to dist_elem:
            # Pop element from GWlist
            # Put in dist_GWlist

# ----------------------------------------------------

# shuf VirusShare