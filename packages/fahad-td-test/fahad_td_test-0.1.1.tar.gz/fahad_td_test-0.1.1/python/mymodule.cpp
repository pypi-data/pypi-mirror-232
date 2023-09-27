#include <boost/python.hpp>
#include "mylib.h"

BOOST_PYTHON_MODULE(mymodule) {
    using namespace boost::python;
    def("add", add);
}
