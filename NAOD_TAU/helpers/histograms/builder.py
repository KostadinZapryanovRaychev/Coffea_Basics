import hist


def make_1d_histogram(name, values, bins, low, high):
    h = hist.Hist.new.Reg(bins, low, high, name=name).Weight()
    h.fill(**{name: values})
    return h


def make_2d_histogram(x_name, x_values, x_bins, x_low, x_high, y_name, y_values, y_bins, y_low, y_high):
    h = hist.Hist.new.Reg(x_bins, x_low, x_high, name=x_name).Reg(y_bins, y_low, y_high, name=y_name).Weight()
    h.fill(**{x_name: x_values, y_name: y_values})
    return h
