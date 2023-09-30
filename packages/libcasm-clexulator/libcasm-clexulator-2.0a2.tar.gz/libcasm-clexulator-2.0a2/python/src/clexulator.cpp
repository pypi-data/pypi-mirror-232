#include <pybind11/eigen.h>
#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

// nlohmann::json binding
#define JSON_USE_IMPLICIT_CONVERSIONS 0
#include "pybind11_json/pybind11_json.hpp"

// CASM
#include "casm/casm_io/Log.hh"
#include "casm/casm_io/json/InputParser_impl.hh"
#include "casm/casm_io/json/jsonParser.hh"
#include "casm/clexulator/BaseClexulator.hh"
#include "casm/clexulator/Clexulator.hh"
#include "casm/clexulator/ClusterExpansion.hh"
#include "casm/clexulator/ConfigDoFValuesTools_impl.hh"
#include "casm/clexulator/Correlations.hh"
#include "casm/clexulator/DoFSpace.hh"
#include "casm/clexulator/LocalClusterExpansion.hh"
#include "casm/clexulator/LocalCorrelations.hh"
#include "casm/clexulator/NeighborList.hh"
#include "casm/clexulator/OrderParameter.hh"
#include "casm/clexulator/SparseCoefficients.hh"
#include "casm/clexulator/io/json/Clexulator_json_io.hh"
#include "casm/clexulator/io/json/ConfigDoFValues_json_io.hh"
#include "casm/clexulator/io/json/DoFSpace_json_io.hh"
#include "casm/clexulator/io/json/SparseCoefficients_json_io.hh"

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

namespace py = pybind11;

/// CASM - Python binding code
namespace CASMpy {

using namespace CASM;

struct PrimDoFInfo {
  PrimDoFInfo(xtal::BasicStructure const &basic_structure)
      : n_sublat(basic_structure.basis().size()),
        global_dof_info(clexulator::make_global_dof_info(basic_structure)),
        local_dof_info(clexulator::make_local_dof_info(basic_structure)) {}

  Index n_sublat;
  std::map<DoFKey, xtal::DoFSet> global_dof_info;
  std::map<DoFKey, std::vector<xtal::SiteDoFSet>> local_dof_info;
};

// Need to allow constructing empty
// std::shared_ptr<clexulator::PrimNeighborList>, but PyBind11 won't allow it,
// so use this wrapper class
struct PrimNeighborListWrapper {
  std::shared_ptr<clexulator::PrimNeighborList> prim_neighbor_list;
};

std::shared_ptr<PrimNeighborListWrapper> make_prim_neighbor_list(
    std::optional<Eigen::Matrix3l> const &weight_matrix,
    std::optional<std::vector<int>> sublattice_indices,
    std::optional<int> total_n_sublattice) {
  auto wrapper = std::make_shared<PrimNeighborListWrapper>();
  if (!weight_matrix.has_value()) {
    return wrapper;
  }

  std::set<int> _sublattice_indices(sublattice_indices.value().begin(),
                                    sublattice_indices.value().end());
  wrapper->prim_neighbor_list = std::make_shared<clexulator::PrimNeighborList>(
      weight_matrix.value(), _sublattice_indices.begin(),
      _sublattice_indices.end(), total_n_sublattice.value());
  return wrapper;
}

std::shared_ptr<clexulator::SuperNeighborList> make_super_neighbor_list(
    Eigen::Matrix3l const &transformation_matrix_to_super,
    PrimNeighborListWrapper const &wrapper) {
  if (wrapper.prim_neighbor_list == nullptr) {
    throw std::runtime_error(
        "Error in make_super_neighbor_list: prim_neighbor_list is not "
        "initialized");
  }
  return std::make_shared<clexulator::SuperNeighborList>(
      transformation_matrix_to_super, *wrapper.prim_neighbor_list);
}

std::shared_ptr<clexulator::Clexulator> make_empty_clexulator() {
  return std::make_shared<clexulator::Clexulator>();
}

std::shared_ptr<clexulator::Clexulator> make_clexulator(
    std::string source, std::shared_ptr<PrimNeighborListWrapper> wrapper,
    std::optional<std::string> compile_options,
    std::optional<std::string> so_options) {
  // Use JSON parser to avoid duplication and give nice error messages
  jsonParser json;
  json["source"] = source;
  if (compile_options.has_value()) {
    json["compile_options"] = compile_options.value();
  }
  if (so_options.has_value()) {
    json["so_options"] = compile_options.value();
  }
  InputParser<clexulator::Clexulator> parser(json, wrapper->prim_neighbor_list);
  std::runtime_error error_if_invalid{
      "Error in libcasm.clexulator.make_clexulator"};
  report_and_throw_if_invalid(parser, CASM::log(), error_if_invalid);
  return std::make_shared<clexulator::Clexulator>(std::move(*parser.value));
}

struct LocalClexulatorWrapper {
  std::shared_ptr<std::vector<clexulator::Clexulator>> local_clexulator;
};

std::shared_ptr<LocalClexulatorWrapper> make_empty_local_clexulator() {
  auto lclex_wrapper = std::make_shared<LocalClexulatorWrapper>();
  lclex_wrapper->local_clexulator =
      std::make_shared<std::vector<clexulator::Clexulator>>();
  return lclex_wrapper;
}

std::shared_ptr<LocalClexulatorWrapper> make_local_clexulator(
    std::string source, std::shared_ptr<PrimNeighborListWrapper> wrapper,
    std::optional<std::string> compile_options,
    std::optional<std::string> so_options) {
  // Use JSON parser to avoid duplication and give nice error messages
  jsonParser json;
  json["source"] = source;
  if (compile_options.has_value()) {
    json["compile_options"] = compile_options.value();
  }
  if (so_options.has_value()) {
    json["so_options"] = compile_options.value();
  }
  InputParser<std::vector<clexulator::Clexulator>> parser(
      json, wrapper->prim_neighbor_list);
  std::runtime_error error_if_invalid{
      "Error in libcasm.clexulator.make_local_clexulator"};
  report_and_throw_if_invalid(parser, CASM::log(), error_if_invalid);

  auto lclex_wrapper = std::make_shared<LocalClexulatorWrapper>();
  lclex_wrapper->local_clexulator =
      std::make_shared<std::vector<clexulator::Clexulator>>(
          std::move(*parser.value));
  return lclex_wrapper;
}

std::shared_ptr<clexulator::Correlations> make_correlations(
    std::shared_ptr<clexulator::SuperNeighborList const> const
        &supercell_neighbor_list,
    std::shared_ptr<clexulator::Clexulator const> const &clexulator,
    clexulator::ConfigDoFValues const *dof_values,
    std::optional<std::vector<unsigned int>> correlation_indices) {
  if (correlation_indices.has_value()) {
    return std::make_shared<clexulator::Correlations>(
        supercell_neighbor_list, clexulator, correlation_indices.value(),
        dof_values);
  } else {
    return std::make_shared<clexulator::Correlations>(supercell_neighbor_list,
                                                      clexulator, dof_values);
  }
}

std::shared_ptr<clexulator::LocalCorrelations> make_local_correlations(
    std::shared_ptr<clexulator::SuperNeighborList const> const
        &supercell_neighbor_list,
    std::shared_ptr<LocalClexulatorWrapper> const &local_clexulator_wrapper,
    clexulator::ConfigDoFValues const *dof_values,
    std::optional<std::vector<unsigned int>> correlation_indices) {
  if (correlation_indices.has_value()) {
    return std::make_shared<clexulator::LocalCorrelations>(
        supercell_neighbor_list, local_clexulator_wrapper->local_clexulator,
        correlation_indices.value(), dof_values);
  } else {
    return std::make_shared<clexulator::LocalCorrelations>(
        supercell_neighbor_list, local_clexulator_wrapper->local_clexulator,
        dof_values);
  }
}

std::shared_ptr<clexulator::ClusterExpansion> make_cluster_expansion(
    std::shared_ptr<clexulator::SuperNeighborList const> const
        &supercell_neighbor_list,
    std::shared_ptr<clexulator::Clexulator const> const &clexulator,
    clexulator::SparseCoefficients const &coefficients,
    clexulator::ConfigDoFValues const *dof_values) {
  return std::make_shared<clexulator::ClusterExpansion>(
      supercell_neighbor_list, clexulator, coefficients, dof_values);
}

std::shared_ptr<clexulator::MultiClusterExpansion> make_multi_cluster_expansion(
    std::shared_ptr<clexulator::SuperNeighborList const> const
        &supercell_neighbor_list,
    std::shared_ptr<clexulator::Clexulator const> const &clexulator,
    std::vector<clexulator::SparseCoefficients> const &coefficients,
    clexulator::ConfigDoFValues const *dof_values) {
  return std::make_shared<clexulator::MultiClusterExpansion>(
      supercell_neighbor_list, clexulator, coefficients, dof_values);
}

std::shared_ptr<clexulator::LocalClusterExpansion> make_local_cluster_expansion(
    std::shared_ptr<clexulator::SuperNeighborList const> const
        &supercell_neighbor_list,
    std::shared_ptr<LocalClexulatorWrapper> const &local_clexulator_wrapper,
    clexulator::SparseCoefficients const &coefficients,
    clexulator::ConfigDoFValues const *dof_values) {
  return std::make_shared<clexulator::LocalClusterExpansion>(
      supercell_neighbor_list, local_clexulator_wrapper->local_clexulator,
      coefficients, dof_values);
}

std::shared_ptr<clexulator::MultiLocalClusterExpansion>
make_multi_local_cluster_expansion(
    std::shared_ptr<clexulator::SuperNeighborList const> const
        &supercell_neighbor_list,
    std::shared_ptr<LocalClexulatorWrapper> const &local_clexulator_wrapper,
    std::vector<clexulator::SparseCoefficients> const &coefficients,
    clexulator::ConfigDoFValues const *dof_values) {
  return std::make_shared<clexulator::MultiLocalClusterExpansion>(
      supercell_neighbor_list, local_clexulator_wrapper->local_clexulator,
      coefficients, dof_values);
}

clexulator::DoFSpaceAxisInfo make_dof_space_axis_info(
    std::string const &dof_key, xtal::BasicStructure const &prim,
    std::optional<Eigen::Matrix3l> transformation_matrix_to_super,
    std::optional<std::set<Index>> sites) {
  return clexulator::DoFSpaceAxisInfo(dof_key, prim,
                                      transformation_matrix_to_super, sites);
}

std::shared_ptr<clexulator::DoFSpace> make_dof_space(
    std::string const &dof_key,
    std::shared_ptr<xtal::BasicStructure const> const &prim,
    std::optional<Eigen::Matrix3l> transformation_matrix_to_super,
    std::optional<std::set<Index>> sites,
    std::optional<Eigen::MatrixXd> basis) {
  return std::make_shared<clexulator::DoFSpace>(
      dof_key, prim, transformation_matrix_to_super, sites, basis);
}

}  // namespace CASMpy

PYBIND11_DECLARE_HOLDER_TYPE(T, std::shared_ptr<T>);

PYBIND11_MODULE(_clexulator, m) {
  using namespace CASMpy;

  m.doc() = R"pbdoc(
        Methods for evaluating functions of configurations

        libcasm.clexulator
        ------------------

        The libcasm.clexulator package has a data structure for storing configuration degree of freedom (DoF) values, and methods for evaluating cluster expansion basis functions, order parameters, and other functions of a configuration.

    )pbdoc";
  py::module::import("libcasm.xtal");

  py::class_<clexulator::ConfigDoFValues>(m, "ConfigDoFValues", R"pbdoc(
      Data structure holding occupation, local, and global degree of freedom (DoF) values.

      Notes
      -----

      - ConfigDoFValues may be copied with `copy.copy` or `copy.deepcopy`.

      )pbdoc")
      .def(py::init<>(),
           R"pbdoc(
          Construct uninitialized ConfigDoFValues
          )pbdoc")
      .def(
          "occupation",
          [](clexulator::ConfigDoFValues const &dof_values)
              -> Eigen::VectorXi const & { return dof_values.occupation; },
          py::return_value_policy::reference_internal,
          "Returns the site occupation values, as indices into the allowed "
          "occupants on the corresponding basis site, as a const reference.")
      .def(
          "set_occupation",
          [](clexulator::ConfigDoFValues &dof_values,
             Eigen::Ref<Eigen::VectorXi const> occupation) {
            return dof_values.occupation = occupation;
          },
          "Sets the site occupation values, using a copy.")
      .def(
          "occ",
          [](clexulator::ConfigDoFValues const &dof_values, Index l) -> int {
            return dof_values.occupation(l);
          },
          py::arg("l"),
          "Returns the site occupation value on the specified site, using a "
          "copy.")
      .def(
          "set_occ",
          [](clexulator::ConfigDoFValues &dof_values, Index l, int s) {
            dof_values.occupation(l) = s;
          },
          py::arg("l"), py::arg("s"),
          "Set the site occupation value on site `l` to value `s`. Values are "
          "not checked for validity.")
      .def(
          "global_dof_keys",
          [](clexulator::ConfigDoFValues const &dof_values) {
            std::vector<std::string> keys;
            for (auto const &dof : dof_values.global_dof_values) {
              keys.push_back(dof.first);
            }
            return keys;
          },
          "Returns global DoF keys.")
      .def(
          "global_dof_values",
          [](clexulator::ConfigDoFValues const &dof_values,
             std::string key) -> Eigen::VectorXd const & {
            return dof_values.global_dof_values.at(key);
          },
          py::return_value_policy::reference_internal, py::arg("key"),
          "Returns global DoF values of type `key`, as a const reference.")
      .def(
          "set_global_dof_values",
          [](clexulator::ConfigDoFValues &dof_values, std::string key,
             Eigen::Ref<Eigen::VectorXd const> value) {
            dof_values.global_dof_values.at(key) = value;
          },
          py::arg("key"), py::arg("value"),
          "Set global DoF values of type `key`, using a copy. Key must already "
          "exist.")
      .def(
          "insert_or_assign_global_dof_values",
          [](clexulator::ConfigDoFValues &dof_values, std::string key,
             Eigen::Ref<Eigen::VectorXd const> value) {
            dof_values.global_dof_values.insert_or_assign(key, value);
          },
          py::arg("key"), py::arg("value"),
          "Insert or assign global DoF values of type `key`, using a copy.")
      .def(
          "local_dof_keys",
          [](clexulator::ConfigDoFValues const &dof_values) {
            std::vector<std::string> keys;
            for (auto const &dof : dof_values.local_dof_values) {
              keys.push_back(dof.first);
            }
            return keys;
          },
          "Returns local DoF keys.")
      .def(
          "local_dof_values",
          [](clexulator::ConfigDoFValues const &dof_values,
             std::string key) -> Eigen::MatrixXd const & {
            return dof_values.local_dof_values.at(key);
          },
          py::return_value_policy::reference_internal, py::arg("key"),
          "Returns local DoF values of type `key`, as a const reference.")
      .def(
          "set_local_dof_values",
          [](clexulator::ConfigDoFValues &dof_values, std::string key,
             Eigen::Ref<Eigen::MatrixXd const> value) {
            dof_values.local_dof_values.at(key) = value;
          },
          py::arg("key"), py::arg("value"),
          "Set local DoF values of type `key`, using a copy. Key must already "
          "exist.")
      .def(
          "insert_or_assign_local_dof_values",
          [](clexulator::ConfigDoFValues &dof_values, std::string key,
             Eigen::Ref<Eigen::MatrixXd const> value) {
            dof_values.local_dof_values.insert_or_assign(key, value);
          },
          py::arg("key"), py::arg("value"),
          "Insert or assign local DoF values of type `key`, using a copy.")
      .def(
          "local_dof_site_value",
          [](clexulator::ConfigDoFValues const &dof_values, std::string key,
             Index l) { return dof_values.local_dof_values.at(key).col(l); },
          py::arg("key"), py::arg("l"),
          "Returns local DoF values of type `key` on site `l`, using a copy.")
      .def(
          "set_local_dof_site_value",
          [](clexulator::ConfigDoFValues &dof_values, std::string key, Index l,
             Eigen::Ref<Eigen::VectorXd const> site_dof_value) {
            dof_values.local_dof_values.at(key).col(l) = site_dof_value;
          },
          py::arg("key"), py::arg("l"), py::arg("site_dof_value"),
          "Set the local DoF values of type `key` on site `l`, using a copy. "
          "Key must "
          "already exist.")
      .def(
          "set",
          [](clexulator::ConfigDoFValues &self,
             clexulator::ConfigDoFValues const &other) { self = other; },
          "Assign all values from other, using copy", py::arg("other"))
      .def_static(
          "from_dict",
          [](const nlohmann::json &data) {
            jsonParser json{data};
            InputParser<clexulator::ConfigDoFValues> parser(json);
            std::runtime_error error_if_invalid{
                "Error in libcasm.clexulator.ConfigDoFValues.from_dict"};
            report_and_throw_if_invalid(parser, CASM::log(), error_if_invalid);
            return std::move(*parser.value);
          },
          R"pbdoc(
          Construct ConfigDoFValues from a Python dict

          Notes
          -----
          - This function does not convert ConfigDoFValues between prim and standard bases, it reads values as they are.
          - Conversions, if necessary, must be done after construction using:

              - :func:`~libcasm.clexulator.from_standard_values`: Copy ConfigDoFValues and convert from the standard basis to the prim basis.
              - :func:`~libcasm.clexulator.to_standard_values`: Copy ConfigDoFValues and convert from the prim basis to the standard basis.

          - For a description of the format, see `ConfigDoF JSON object`_

          .. _`ConfigDoF JSON object`: https://prisms-center.github.io/CASMcode_docs/formats/casm/clex/Configuration/#configdof-json-object

          )pbdoc",
          py::arg("data"))
      .def(
          "to_dict",
          [](clexulator::ConfigDoFValues const &values) {
            jsonParser json;
            to_json(values, json);
            return static_cast<nlohmann::json>(json);
          },
          R"pbdoc(
          Represent ConfigDoFValues as a Python dict

          Notes
          -----
          - This function does not convert ConfigDoFValues between prim and standard bases, it writes values as they are.
          - Conversions, if necessary, must be done beforehand using:

              - :func:`~libcasm.clexulator.from_standard_values`: Copy ConfigDoFValues and convert from the standard basis to the prim basis.
              - :func:`~libcasm.clexulator.to_standard_values`: Copy ConfigDoFValues and convert from the prim basis to the standard basis.

          - For a description of the format, see `ConfigDoF JSON object`_

          .. _`ConfigDoF JSON object`: https://prisms-center.github.io/CASMcode_docs/formats/casm/clex/Configuration/#configdof-json-object

          )pbdoc")
      .def("__copy__",
           [](clexulator::ConfigDoFValues const &self) {
             return clexulator::ConfigDoFValues(self);
           })
      .def("__deepcopy__", [](clexulator::ConfigDoFValues const &self) {
        return clexulator::ConfigDoFValues(self);
      });

  m.def(
      "make_default_standard_config_dof_values",
      [](xtal::BasicStructure const &xtal_prim, Index n_unitcells) {
        PrimDoFInfo dof_info(xtal_prim);
        return clexulator::make_default_standard_config_dof_values(
            dof_info.n_sublat, n_unitcells, dof_info.global_dof_info,
            dof_info.local_dof_info);
      },
      "Make ConfigDoFValues, expressed in the standard basis, initialized with "
      "value zero.",
      py::arg("xtal_prim"), py::arg("n_unitcells"));

  m.def(
      "make_default_config_dof_values",
      [](xtal::BasicStructure const &xtal_prim, Index n_unitcells) {
        PrimDoFInfo dof_info(xtal_prim);
        return clexulator::make_default_config_dof_values(
            dof_info.n_sublat, n_unitcells, dof_info.global_dof_info,
            dof_info.local_dof_info);
      },
      "Make ConfigDoFValues, expressed in the prim basis, initialized with "
      "value zero.",
      py::arg("xtal_prim"), py::arg("n_unitcells"));

  m.def(
      "to_standard_values",
      [](clexulator::ConfigDoFValues const &dof_values,
         xtal::BasicStructure const &xtal_prim, Index n_unitcells) {
        PrimDoFInfo dof_info(xtal_prim);
        return clexulator::to_standard_values(
            dof_values, dof_info.n_sublat, n_unitcells,
            dof_info.global_dof_info, dof_info.local_dof_info);
      },
      "Copy ConfigDoFValues and convert from the prim basis to the standard "
      "basis.",
      py::arg("dof_values"), py::arg("xtal_prim"), py::arg("n_unitcells"));

  m.def(
      "from_standard_values",
      [](clexulator::ConfigDoFValues const &dof_values,
         xtal::BasicStructure const &xtal_prim, Index n_unitcells) {
        PrimDoFInfo dof_info(xtal_prim);
        return clexulator::from_standard_values(
            dof_values, dof_info.n_sublat, n_unitcells,
            dof_info.global_dof_info, dof_info.local_dof_info);
      },
      "Copy ConfigDoFValues and convert from the standard basis to the prim "
      "basis.",
      py::arg("dof_values"), py::arg("xtal_prim"), py::arg("n_unitcells"));

  py::class_<PrimNeighborListWrapper, std::shared_ptr<PrimNeighborListWrapper>>(
      m, "PrimNeighborList", R"pbdoc(
      A neighbor list, generated for a Prim, relative to the origin unit cell.

      The PrimNeighborList defines indices to use to reference a site relative
      to a particular unit cell. These can be used to write functions of site
      degrees of freedom (DoF) in terms of a local environment that do not
      depend on the choice of supercell. The PrimNeighborList is then used to
      construct a SuperNeighborList, which defines a neighbor list for a
      particular supercell in terms of linear site indices in that supercell.
      )pbdoc")
      .def(py::init(&make_prim_neighbor_list),
           R"pbdoc(
          Constructor

          Parameters
          ----------
          lattice_weight_matrix : Optional[array_like] = None
              If `lattice_weight_matrix` is None (default), then an
              empty PrimNeighborList is constructed, which will be
              populated appropriately when the first Clexulator is
              constructed. Otherwise, the `lattice_weight_matrix`
              can be specified explicitly.

              In the neighbor list, unit cells are ordered by the distance,
              :math:`x^{\mathsf{T} W x`, where :math:`x` is the integer
              unit cell coordinates, and :math:`W` is the lattice weight
              matrix.

              An appropriate value for the weight matrix of a given lattice
              can be generated using
              :func:`~libcasm.clexulator.PrimNeighborList.make_weight_matrix`.

              In a Clexulator, cluster expansion basis functions are written
              using a particular choice of neighbor list and are incorrect
              if a different lattice weight matrix is used. Therefore,
              the value of the lattice weight matrix is stored in the
              Clexulator file and can be obtained using
              :func:`~libcasm.clexulator.Clexulator.weight_matrix`.
          sublattice_indices: Optional[list[int]] = None
              Sublattice indices of sites that are included in the neighbor
              list. Allows skipping sublattices that have no degrees of
              freedom (DoF). Required when `lattice_weight_matrix` is provided.
          total_n_sublattice: Optional[int] = None
              The total number of sublattices in the relevant Prim.
              Required when `lattice_weight_matrix` is provided.

          )pbdoc",
           py::arg("lattice_weight_matrix") = std::nullopt,
           py::arg("sublattice_indices") = std::nullopt,
           py::arg("total_n_sublattice") = std::nullopt)
      .def_static("make_weight_matrix",
                  &clexulator::PrimNeighborList::make_weight_matrix,
                  R"pbdoc(
          Make a PrimNeighborList weighting matrix appropriate for a
          particular lattice

          Parameters
          ----------
          lattice_column_vector_matrix : array_like, shape=(3,3)
              Lattice vectors as columns of a matrix
          max_element_value: int = 10
              Maximum weight matrix element value
          tol: float = libcasm.xtal.TOL
              Floating point tolerance

          Returns
          -------
          lattice_weight_matrix: array_like, shape=(3,3), dtype=int
              Weight matrix, that defines the shape of neighborhood that
              orders neighbors. In the
              :class:`~libcasm.clexulator.PrimNeighborList`, unit cells
              are ordered by the distance, :math:`x^{\mathsf{T} W x`,
              where :math:`x` is the integer unit cell coordinates. The
              weight matrix is constructed such that
              :math:`x^{\mathsf{T} W x` is approximately spherical in
              Cartesian coordinates, subject to the `max_element_value`.
          )pbdoc",
                  py::arg("lattice_column_vector_matrix"),
                  py::arg("max_element_value") = 10, py::arg("tol") = CASM::TOL)
      .def(
          "sublattice_indices",
          [](PrimNeighborListWrapper const &x) {
            return x.prim_neighbor_list->sublat_indices();
          },
          R"pbdoc(
          Indices of sublattices included in the neighbor list.
        )pbdoc");

  py::class_<clexulator::SuperNeighborList,
             std::shared_ptr<clexulator::SuperNeighborList>>(
      m, "SuperNeighborList", R"pbdoc(
      A supercell-specific neighbor list

      Given a PrimNeighborList, the SuperNeighborList gives the associated
      linear site indices for a particular supercell, for each unit cell in
      the supercell.
      )pbdoc")
      .def(py::init(&make_super_neighbor_list),
           R"pbdoc(
          Constructor

          Parameters
          ----------
          transformation_matrix_to_super: numpy.ndarray[numpy.int64[3, 3]]
              The integer tranformation matrix T such that S = L @ T, where
              S and L are the lattice vectors, as columns of a matrix, of
              the superlattice and prim lattice, respectively.

          prim_neighbor_list: PrimNeighborList
              The PrimNeighborList used to determine the SuperNeighborList
              linear site indices.

          )pbdoc",
           py::arg("transformation_matrix_to_super"),
           py::arg("prim_neighbor_list"))
      .def("overlaps", &clexulator::SuperNeighborList::overlaps,
           R"pbdoc(
          Returns true if periodic images of the neighbor list overlap

          Returns
          -------
          result: PrimNeighborList
              If periodic images of the neighborhood overlap, Clexulator 'delta' values must be calculated from the difference between final and initial point values.

          )pbdoc");

  py::class_<clexulator::Clexulator, std::shared_ptr<clexulator::Clexulator>>(
      m, "Clexulator", R"pbdoc(
      Evaluate basis set functions

      CASM generates code for very efficient calculation of basis functions.
      This source code may be compiled, linked, and used at runtime via Clexulator.
      )pbdoc")
      .def(py::init(&make_empty_clexulator),
           R"pbdoc(
          Construct an empty Clexulator

          Use the factory function :func:`~libcasm.clexulator.make_clexulator` to construct Clexulator from a clexulator source code file.
          )pbdoc")
      .def(
          "n_functions",
          [](clexulator::Clexulator const &clexulator) {
            return clexulator.corr_size();
          },
          "Return the number of basis functions")
      .def(
          "n_point_corr",
          [](clexulator::Clexulator const &clexulator) {
            return clexulator.n_point_corr();
          },
          "Return point correlations")
      .def(
          "weight_matrix",
          [](clexulator::Clexulator const &clexulator) {
            return clexulator.weight_matrix();
          },
          "Weight matrix used for ordering the neighbor list")
      .def(
          "n_sublattices",
          [](clexulator::Clexulator const &clexulator) {
            return clexulator.n_sublattices();
          },
          "Total number of sublattices in the Prim")
      .def(
          "nlist_size",
          [](clexulator::Clexulator const &clexulator) {
            return clexulator.nlist_size();
          },
          "Total number of sublattices in the Prim")
      .def(
          "sublat_indices",
          [](clexulator::Clexulator const &clexulator) {
            return clexulator.sublat_indices();
          },
          "Sublat indices in the Prim");
  //
  py::class_<LocalClexulatorWrapper, std::shared_ptr<LocalClexulatorWrapper>>(
      m, "LocalClexulator", R"pbdoc(
      Evaluate local basis set functions

      CASM generates code for very efficient calculation of basis functions.
      This source code may be compiled, linked, and used at runtime via Clexulator.
      The LocalClexulator contains one Clexulator for each equivalent local basis set.
      )pbdoc")
      .def(py::init(&make_empty_local_clexulator),
           R"pbdoc(
          Construct an empty LocalClexulator

          Use the factory function :func:`~libcasm.clexulator.make_local_clexulator` to construct LocalClexulator from clexulator source code files.
          )pbdoc")
      .def(
          "n_functions",
          [](LocalClexulatorWrapper const &wrapper) {
            return wrapper.local_clexulator->at(0).corr_size();
          },
          "Return the number of basis functions")
      .def(
          "n_equivalents",
          [](LocalClexulatorWrapper const &wrapper) {
            return wrapper.local_clexulator->size();
          },
          "Return the number of equivalent local basis sets");

  m.def("make_clexulator", &make_clexulator,
        R"pbdoc(
      Construct a Clexulator, if necessary compiling from source code

      Parameters
      ----------
      source: str
          Path to a Clexulator source file implementing a basis set.

      prim_neighbor_list: PrimNeighborList
          The PrimNeighborList is expanded as necessary for use with
          the Clexulator.

      compile_options: str = None
          Options used to compile the Clexulator source file, if it is not yet
          compiled. Example: "g++ -O3 -Wall -fPIC --std=c++17 -I/path/to/include".
          The default values can be configured with:

              CASM_CXX:
                  Set compiler; default="g++"
              CASM_CXXFLAGS:
                  Set compiler flags; default="-O3 -Wall -fPIC --std=c++17"
              CASM_INCLUDEDIR:
                  Set include search path, overriding CASM_PREFIX
              CASM_PREFIX:
                  Set include search path to -I$CASM_PREFIX/include; default
                  tries to find "ccasm" or "casm" executables on PATH and
                  checks relative locations

      so_options: str = None
          Options used to compile the Clexulator shared object file, if it is not
          yet compiled. Example: "g++ -shared -L/path/to/lib -lcasm_clexulator "

          The default values can be configured with:

              CASM_CXX:
                  Set compiler; default="g++"
              CASM_SOFLAGS:
                  Set shared object compilation flags; default="-shared"
              CASM_LIBDIR:
                  Set link search path, overriding CASM_PREFIX
              CASM_PREFIX:
                  Set include search path to -L$CASM_PREFIX/lib; default
                  tries to find "ccasm" or "casm" executables on PATH and
                  checks relative locations

      Returns
      -------
      clexulator: Clexulator
          The Clexulator.

      )pbdoc",
        py::arg("source"), py::arg("prim_neighbor_list"),
        py::arg("compile_options") = std::nullopt,
        py::arg("so_options") = std::nullopt);

  m.def("make_local_clexulator", &make_local_clexulator,
        R"pbdoc(
      Construct a :class:`~libcasm.clexulator.LocalClexulator`, if necessary compiling from source code

      Parameters
      ----------
      source: str
          Path to a prototype local clexulator source file. Clexulator source files for symmetric equivalents are expected to be found relative to the prototype file.

      prim_neighbor_list: PrimNeighborList
          The PrimNeighborList is expanded as necessary for use with
          the Clexulator.

      compile_options: str = None
          Options used to compile the clexulator source files, if it they are not yet
          compiled. Example: "g++ -O3 -Wall -fPIC --std=c++17 -I/path/to/include".
          The default values can be configured with:

              CASM_CXX:
                  Set compiler; default="g++"
              CASM_CXXFLAGS:
                  Set compiler flags; default="-O3 -Wall -fPIC --std=c++17"
              CASM_INCLUDEDIR:
                  Set include search path, overriding CASM_PREFIX
              CASM_PREFIX:
                  Set include search path to -I$CASM_PREFIX/include; default
                  tries to find "ccasm" or "casm" executables on PATH and
                  checks relative locations

      so_options: str = None
          Options used to compile the clexulator shared object files, if they are not
          yet compiled. Example: "g++ -shared -L/path/to/lib -lcasm_clexulator "

          The default values can be configured with:

              CASM_CXX:
                  Set compiler; default="g++"
              CASM_SOFLAGS:
                  Set shared object compilation flags; default="-shared"
              CASM_LIBDIR:
                  Set link search path, overriding CASM_PREFIX
              CASM_PREFIX:
                  Set include search path to -L$CASM_PREFIX/lib; default
                  tries to find "ccasm" or "casm" executables on PATH and
                  checks relative locations

      Returns
      -------
      local_clexulator: LocalClexulator
          A :class:`~libcasm.clexulator.LocalClexulator` that allows evaluating
          the symmetrically equivalent local basis sets.

      )pbdoc",
        py::arg("source"), py::arg("prim_neighbor_list"),
        py::arg("compile_options") = std::nullopt,
        py::arg("so_options") = std::nullopt);

  m.def(
      "calc_intensive_correlations",
      [](std::shared_ptr<clexulator::Clexulator> const &clexulator,
         clexulator::ConfigDoFValues const &config_dof_values,
         std::shared_ptr<clexulator::SuperNeighborList const> const
             &supercell_neighbor_list,
         std::optional<std::vector<unsigned int>> indices) {
        if (!clexulator->initialized()) {
          throw std::runtime_error(
              "Error in calc_intensive_correlations: clexulator is not "
              "initialized");
        }
        if (indices.has_value()) {
          clexulator::Correlations f(supercell_neighbor_list, clexulator,
                                     *indices, &config_dof_values);
          return f.intensive(f.extensive());
        } else {
          clexulator::Correlations f(supercell_neighbor_list, clexulator,
                                     &config_dof_values);
          return f.intensive(f.extensive());
        }
      },
      R"pbdoc(
      Calculate intensive correlations

      This method is safe and easy to use, but may be slower than using
      the :class:`~libcasm.clexulator.Correlations` class directly.

      Parameters
      ----------
      clexulator: Clexulator
          The Clexulator used to evaluate basis functions
      config_dof_values: ConfigDoFValues
          Configuration degree of freedom (DoF) values input to the basis functions.
      supercell_neighbor_list: SuperNeighborList
          The SuperNeighborList for the supercell consistent with `config_dof_values`.
      indices: Optional[list[int]] = None
          If provided, only calculate the basis functions with corresponding
          indices. The same size correlation array is always returned, but other
          values will be of undefined value.

      Returns
      -------
      intensive_correlations: np.ndarray
          The correlations, normalized per unit cell.

      )pbdoc",
      py::arg("supercell_neighbor_list"), py::arg("clexulator"),
      py::arg("config_dof_values"), py::arg("indices") = std::nullopt);

  m.def(
      "calc_local_correlations",
      [](LocalClexulatorWrapper const &wrapper,
         clexulator::ConfigDoFValues const &config_dof_values,
         std::shared_ptr<clexulator::SuperNeighborList const> const
             &supercell_neighbor_list,
         Index unitcell_index, Index equivalent_index,
         std::optional<std::vector<unsigned int>> indices) {
        if (wrapper.local_clexulator->size() == 0) {
          throw std::runtime_error(
              "Error in calc_local_correlations: local_clexulator is not "
              "initialized");
        }
        if (indices.has_value()) {
          clexulator::LocalCorrelations f(supercell_neighbor_list,
                                          wrapper.local_clexulator, *indices,
                                          &config_dof_values);
          return f.local(unitcell_index, equivalent_index);
        } else {
          clexulator::LocalCorrelations f(supercell_neighbor_list,
                                          wrapper.local_clexulator,
                                          &config_dof_values);
          return f.local(unitcell_index, equivalent_index);
        }
      },
      R"pbdoc(
      Calculate local correlations

      This method is safe and easy to use, but may be slower than using
      the :class:`~libcasm.clexulator.LocalCorrelations` class directly.

      Parameters
      ----------
      local_clexulator: LocalClexulator
          The LocalClexulator used to evaluate local basis functions
      config_dof_values: ConfigDoFValues
          Configuration degree of freedom (DoF) values input to the basis functions.
      supercell_neighbor_list: SuperNeighborList
          The SuperNeighborList for the supercell consistent with `config_dof_values`.
      unitcell_index: int
          Linear unit cell index specifying in which unit cell to evaluate the
          local correlations.
      equivalent_index: int
          Index indicating which of the symmetrically local cluster basis sets
          to evaluate.
      indices: Optional[list[int]] = None
          If provided, only calculate the basis functions with corresponding
          indices. The same size correlation array is always returned, but other
          values will be of undefined value.
      Returns
      -------
      local_correlations: np.ndarray
          The local correlations.

      )pbdoc",
      py::arg("supercell_neighbor_list"), py::arg("local_clexulator"),
      py::arg("config_dof_values"), py::arg("unitcell_index"),
      py::arg("equivalent_index"), py::arg("indices") = std::nullopt);

  py::class_<clexulator::Correlations,
             std::shared_ptr<clexulator::Correlations>>(m, "Correlations",
                                                        R"pbdoc(
      Correlations calculator

      )pbdoc")
      .def(py::init<>(&make_correlations), R"pbdoc(
          Constructor

          Parameters
          ----------
          supercell_neighbor_list: :class:`~libcasm.clexulator.SuperNeighborList`
              The :class:`~libcasm.clexulator.SuperNeighborList` for the supercell consistent with `config_dof_values`.
          clexulator: :class:`~libcasm.clexulator.Clexulator`
              The :class:`~libcasm.clexulator.Clexulator` used to evaluate basis functions
          config_dof_values: ConfigDoFValues
              Configuration degree of freedom (DoF) values input to the basis functions. The Correlations instance stores a pointer to the underlying data, which must have a lifetime as long as ClusterExpansion is used to calculate with its data.
          indices: Optional[list[int]] = None
              If provided, only calculate the basis functions with corresponding
              indices. The same size correlation array is always returned, but other
              values will be of undefined value.

          )pbdoc",
           py::arg("supercell_neighbor_list"), py::arg("clexulator"),
           py::arg("config_dof_values"), py::arg("indices") = std::nullopt)
      .def("set", &clexulator::Correlations::set, R"pbdoc(
          Set the :class:`~libcasm.clexulator.ConfigDoFValues` instance LocalCorrelations uses to calculate the local correlations. LocalCorrelations maintains a pointer to the underlying data, which must have a lifetime as long as LocalCorrelations is used to calculate with its data.
          )pbdoc")
      .def("corr_size", &clexulator::Correlations::corr_size, R"pbdoc(
          Number of correlations.
          )pbdoc")
      .def("indices", &clexulator::Correlations::correlation_indices,
           py::return_value_policy::reference_internal, R"pbdoc(
          The elements of the correlations vector that will be calculated.
          )pbdoc")
      .def("required_update_neighborhood",
           &clexulator::Correlations::required_update_neighborhood, R"pbdoc(
          The coordinates of sites (relative to the origin unit cell) where a change in DoF values requires a local cluster expansions's values to be re-calculated.

          Parameters
          ----------
          equivalent_index: int
              Index indicating which of the symmetrically local cluster basis sets to get the neighborhood for.
          )pbdoc")
      .def("extensive", &clexulator::Correlations::extensive,
           py::return_value_policy::reference_internal, R"pbdoc(
          Calculate and return extensive correlations, as const reference.

          Returns
          -------
          value : np.ndarray
              Extensive correlations (per supercell). The same size correlation array is always returned, but if this instance was constructed with the indices of specific basis functions to calculate other values will be of undefined value.
          )pbdoc")
      .def("intensive", &clexulator::Correlations::intensive,
           py::return_value_policy::reference_internal, R"pbdoc(
          Calculate and return intensive correlations, as const reference.

          Parameters
          ----------
          extensive_correlations: np.ndarray
              Extensive correlations (per supercell), to be normalized by the number of unit cells in the supercell.

          Returns
          -------
          value : np.ndarray
              Intensive correlations  (per unit cell). The same size correlation array is always returned, but if this instance was constructed with the indices of specific basis functions to calculate other values will be of undefined value.
          )pbdoc",
           py::arg("extensive_correlations"))
      .def("contribution", &clexulator::Correlations::contribution,
           py::return_value_policy::reference_internal, R"pbdoc(
          Calculate and return the contribution from a particular unit cell, as const reference.

          Parameters
          ----------
          linear_unitcell_index: int
              Linear unit cell index (as defined by a :class:`~libcasm.xtal.UnitCellIndexConverter`) to calculate correlation contributions from

          Returns
          -------
          value : np.ndarray
              Correlation contribution from a single unit cell. The same size correlation array is always returned, but if this instance was constructed with the indices of specific basis functions to calculate other values will be of undefined value.
          )pbdoc",
           py::arg("linear_unitcell_index"))
      .def("has_point", &clexulator::Correlations::has_point,
           py::return_value_policy::reference_internal, R"pbdoc(
          Calculate and return the contribution from a particular unit cell, as const reference.

          Parameters
          ----------
          linear_site_index: int
              Linear site index (as defined by a :class:`~libcasm.xtal.SiteIndexConverter`).

          Returns
          -------
          result : bool
              True if point correlations can be calculated valid at specified site.
          )pbdoc",
           py::arg("linear_unitcell_index"))
      .def("point", &clexulator::Correlations::point,
           py::return_value_policy::reference_internal, R"pbdoc(
          Calculate and return the correlations at specified point, as const reference.

          Parameters
          ----------
          linear_site_index: int
              Linear site index (as defined by a :class:`~libcasm.xtal.SiteIndexConverter`).
          skip_if_unnecessary_for_occ_delta: bool = False
              If true, skip calculating point correlations if they are not necessary for calculating :func:`~libcasm.clexulator.Correlations.occ_delta`. This will be the case if the supercell is not too small (`supercell_neighbor_list.overlaps() == False`).

          Returns
          -------
          result : np.ndarray
              Sum of all basis functions that include DoF from the specified site, as const reference.
          )pbdoc",
           py::arg("linear_site_index"),
           py::arg("skip_if_unnecessary_for_occ_delta"))
      .def("all_points", &clexulator::Correlations::all_points, R"pbdoc(
          Calculate and return all point correlations, as a matrix

          Parameters
          ----------
          include_all_sites: bool = true
              If true, include a row for every site, even if there are no point correlations associated with that site (in which case the row is all zeros). If false, only include rows are only included for sites from sublattices included in :func:`~libcasm.clexulator.PrimNeighborList.sublattice_indices()` (rows are still ordered according to increasing site index).

          Returns
          -------
          result : np.ndarray
              All point correlations, as rows of a matrix.
          )pbdoc",
           py::arg("include_all_sites"))
      .def("all_points_site_indices",
           &clexulator::Correlations::all_points_site_indices, R"pbdoc(
          Return the site index corresponding to each row of the matrix returned by `all_points`

          Parameters
          ----------
          include_all_sites: bool = true
              If true, include a row for every site, even if there are no point correlations associated with that site (in which case the row is all zeros). If false, only include rows are only included for sites from sublattices included in :func:`~libcasm.clexulator.PrimNeighborList.sublattice_indices()` (rows are still ordered according to increasing site index).

          Returns
          -------
          result : list[int]
              The site index corresponding to each row of the matrix returned by `all_points`.
          )pbdoc",
           py::arg("include_all_sites"))
      .def(
          "occ_delta",
          [](clexulator::Correlations &x, Index linear_site_index, int new_occ,
             Eigen::VectorXd const &reference_point_correlations)
              -> Eigen::VectorXd const & {
            return x.occ_delta(linear_site_index, new_occ,
                               reference_point_correlations);
          },
          py::return_value_policy::reference_internal, R"pbdoc(
          Calculate and return change in (extensive) correlations due to an occupation change

          Parameters
          ----------
          linear_site_index: int
              Linear site indices (as defined by a :class:`~libcasm.xtal.SiteIndexConverter`) where occupant DoF values are changed.
          new_occ: int
              The value the occupant DoF is changed to.
          reference_point_correlations: np.ndarray
              The point correlations of the specified site before the change in occupation value. This value is not needed and ignored if the supercell is large enough (`supercell_neighbor_list.overlaps() == False`).

          Returns
          -------
          delta_value : np.ndarray
              Change in extensive correlations, relative to `reference_point_correlations`.
          )pbdoc",
          py::arg("linear_site_index"), py::arg("new_occ"),
          py::arg("reference_point_correlations"))
      .def(
          "multi_occ_delta",
          [](clexulator::Correlations &x,
             std::vector<Index> const &linear_site_index,
             std::vector<int> const &new_occ) -> Eigen::VectorXd const & {
            return x.occ_delta(linear_site_index, new_occ);
          },
          py::return_value_policy::reference_internal, R"pbdoc(
          Calculate and return change in (extensive) correlations due to multiple occupation changes

          Parameters
          ----------
          linear_site_index: list[int]
              Linear site indices (as defined by a :class:`~libcasm.xtal.SiteIndexConverter`) where occupant DoF values are changed.
          new_occ: list[int]
              The value the occupant DoF are changed to.

          Returns
          -------
          delta_value : np.ndarray
              Change in extensive correlations due to specified occupant changes.
          )pbdoc",
          py::arg("linear_site_index"), py::arg("new_occ"))
      .def("local_delta", &clexulator::Correlations::local_delta,
           py::return_value_policy::reference_internal, R"pbdoc(
          Calculate and return change in (extensive) correlations due to a local DoF change

          Parameters
          ----------
          key: str
              Specifies the type of DoF
          linear_site_index: int
              Linear site indices (as defined by a :class:`~libcasm.xtal.SiteIndexConverter`) where occupant DoF values are changed.
          new_value: np.ndarray
              The value the local DoF is changed to on the specified site, in the prim basis.
          reference_point_correlations: np.ndarray
              The point correlations of the specified site before the change in local DoF value.

          Returns
          -------
          delta_value : np.ndarray
              Change in extensive correlations, relative to `reference_point_correlations`.
          )pbdoc",
           py::arg("key"), py::arg("linear_site_index"), py::arg("new_value"),
           py::arg("reference_point_correlations"))
      .def("global_delta", &clexulator::Correlations::global_delta,
           py::return_value_policy::reference_internal, R"pbdoc(
          Calculate and return change in (extensive) correlations due to a global DoF change

          Parameters
          ----------
          key: str
              Specifies the type of DoF
          new_value: np.ndarray
              The value the global DoF is changed to, in the prim basis.
          reference_extensive_correlations: np.ndarray
              The extensive correlations before the change in global DoF value.

          Returns
          -------
          delta_value : np.ndarray
              Change in extensive correlations, relative to `reference_extensive_correlations`.
          )pbdoc",
           py::arg("key"), py::arg("new_value"),
           py::arg("`reference_extensive_correlations"));

  py::class_<clexulator::LocalCorrelations,
             std::shared_ptr<clexulator::LocalCorrelations>>(
      m, "LocalCorrelations", R"pbdoc(
      Local correlations calculator

      )pbdoc")
      .def(py::init<>(&make_local_correlations), R"pbdoc(
          Constructor

          Parameters
          ----------
          supercell_neighbor_list: :class:`~libcasm.clexulator.SuperNeighborList`
              The :class:`~libcasm.clexulator.SuperNeighborList` for the supercell consistent with `config_dof_values`.
          clexulator: :class:`~libcasm.clexulator.LocalClexulator`
              The :class:`~libcasm.clexulator.LocalClexulator` used to evaluate basis functions
          config_dof_values: ConfigDoFValues
              Configuration degree of freedom (DoF) values input to the basis functions. The LocalCorrelations instance stores a pointer to the underlying data, which must have a lifetime as long as ClusterExpansion is used to calculate with its data.
          indices: Optional[list[int]] = None
              If provided, only calculate the basis functions with corresponding
              indices. The same size correlation array is always returned, but other
              values will be of undefined value.

          )pbdoc",
           py::arg("supercell_neighbor_list"), py::arg("clexulator"),
           py::arg("config_dof_values"), py::arg("indices") = std::nullopt)
      .def("set", &clexulator::LocalCorrelations::set, R"pbdoc(
          Set the :class:`~libcasm.clexulator.ConfigDoFValues` instance LocalCorrelations uses to calculate the local correlations. LocalCorrelations maintains a pointer to the underlying data, which must have a lifetime as long as LocalCorrelations is used to calculate with its data.
          )pbdoc")
      .def("corr_size", &clexulator::LocalCorrelations::corr_size, R"pbdoc(
          Number of correlations.
          )pbdoc")
      .def("indices", &clexulator::LocalCorrelations::correlation_indices,
           py::return_value_policy::reference_internal, R"pbdoc(
          The elements of the correlations vector that will be calculated.
          )pbdoc")
      .def("required_update_neighborhood",
           &clexulator::LocalCorrelations::required_update_neighborhood,
           R"pbdoc(
          The coordinates of sites (relative to the origin unit cell) where a change in DoF values requires a local cluster expansions's values to be re-calculated.

          Parameters
          ----------
          equivalent_index: int
              Index indicating which of the symmetrically local cluster basis sets to get the neighborhood for.
          )pbdoc")
      .def("value", &clexulator::LocalCorrelations::local, R"pbdoc(
          Calculate the local correlations

          Parameters
          ----------
          unitcell_index: int
              Linear unit cell index specifying in which unit cell to evaluate the
              local correlations.
          equivalent_index: int
              Index indicating which of the symmetrically local cluster basis sets
              to evaluate.

          Returns
          -------
          value : np.ndarray
              Local correlations. The same size correlation array is always returned, but if this instance was constructed with the indices of specific basis functions to calculate other values will be of undefined value.
          )pbdoc",
           py::return_value_policy::reference_internal,
           py::arg("unitcell_index"), py::arg("equivalent_index"));

  py::class_<clexulator::SparseCoefficients>(m, "SparseCoefficients", R"pbdoc(
    Container for non-zero expansion coefficients

    Notes
    -----

    - SparseCoefficients may be copied with `copy.copy` or `copy.deepcopy`.
    - The multiplication operator can be used with SparseCoefficients and a vector of correlations:

      .. code-block:: Python

          >>> import numpy as np
          >>> from libcasm.clexulator import SparseCoefficients
          >>> coeff = SparseCoefficients(index=[0, 2], value=[1.1, -0.3])
          >>> correlations = np.array([0.1, 0.1, 0.1, 0.1])
          >>> print(coeff * correlations)
          0.08
          >>> correlations = np.array([0.0, 0.1, 0.1, 0.1])
          >>> print(coeff * correlations)
          -0.03

    )pbdoc")
      .def(py::init<std::vector<unsigned int>, std::vector<double>>(), R"pbdoc(
        Parameters
        ----------
        index: list[int]
            Indices of basis functions with non-zero coefficients
        value: list[float]
            Expansion coefficients, for the basis functions specified by `index`
        )pbdoc",
           py::arg("index") = std::vector<unsigned int>(),
           py::arg("value") = std::vector<double>())
      .def_readwrite("index", &clexulator::SparseCoefficients::index, R"pbdoc(
        list[int]: Indices of basis functions with non-zero coefficients
        )pbdoc")
      .def_readwrite("value", &clexulator::SparseCoefficients::index, R"pbdoc(
        list[float]: Expansion coefficients, for the basis functions specified by `index`
        )pbdoc")
      .def_static(
          "from_data",
          [](const nlohmann::json &data) {
            jsonParser json{data};
            InputParser<clexulator::SparseCoefficients> parser(json);
            std::runtime_error error_if_invalid{
                "Error in libcasm.clexulator.SparseCoefficients.from_dict"};
            report_and_throw_if_invalid(parser, CASM::log(), error_if_invalid);
            return std::move(*parser.value);
          },
          R"pbdoc(
        Construct SparseCoefficients from a JSON-serializeable representation

        Notes
        -----
        - Accepts CASM v1 format (`{"orbits": [...]}`) if "orbits" is present
        - Otherwise, assumes CASM v2 format (`[[index, value], ...]`)

        )pbdoc",
          py::arg("data"))
      .def(
          "to_data",
          [](clexulator::SparseCoefficients const &values) {
            jsonParser json;
            to_json(values, json);
            return static_cast<nlohmann::json>(json);
          },
          R"pbdoc(
        Represent SparseCoefficients as a JSON-serializeable list

        Returns
        -------
        data:
            A list of [index, value] pairs (`[[index, value], ...]`).

        )pbdoc")
      .def(
          "__mul__",
          [](clexulator::SparseCoefficients const &self,
             Eigen::VectorXd const &correlations) {
            return self * correlations;
          },
          R"pbdoc(
        Evaluate cluster expansion value given coefficients and correlations

        Parameters
        ----------
        self: SparseCoefficients
            The expansion coefficients
        correlations: np.ndarray
            The correlations, of size matching the total number of basis functions, so there are values associated with both zero and non-zero expansion coefficients.

        Returns
        -------
        value:
            The result of multiplying coefficients by correlation values and summing.

        )pbdoc",
          py::arg("correlations"))
      .def("__copy__",
           [](clexulator::SparseCoefficients const &self) {
             return clexulator::SparseCoefficients(self);
           })
      .def("__deepcopy__", [](clexulator::SparseCoefficients const &self) {
        return clexulator::SparseCoefficients(self);
      });

  py::class_<clexulator::ClusterExpansion,
             std::shared_ptr<clexulator::ClusterExpansion>>(
      m, "ClusterExpansion", R"pbdoc(
      A cluster expansion calculator

      ClusterExpansion calculates:

      - the value of a cluster expansion
      - the change in the value of a cluster expansion given changes in degree of freedom (DoF) values

      To calculate the cluster expansion value, ClusterExpansion uses:

      - :class:`~libcasm.clexulator.Clexulator`: which evaluates cluster expansion basis functions
      - :class:`~libcasm.clexulator.SuperNeighborList`: which allows Clexulator to find the correct neighbors degree of freedom (DoF) values for each basis function
      - :class:`~libcasm.clexulator.SparseCoefficients`: which provides cluster expansion coefficients
      - :class:`~libcasm.clexulator.ConfigDoFValues`: ClusterExpansion is given a pointer to a ConfigDoFValues instance and calculates the cluster expansion using the current state of the DoF values

      Examples
      --------

      For usage examples, see the section :ref:`Evaluating a cluster expansion <cluster-expansion-index>`.

      Notes
      -----

      - One ClusterExpansion instance is needed to calculate the cluster expansion in each distinct supercell, using the appropriate :class:`~libcasm.clexulator.SuperNeighborList` at construction.

      - The cluster expansion is calculated for a :class:`~libcasm.clexulator.ConfigDoFValues` instance that can be given at construction or using the :func:`~libcasm.clexulator.ClusterExpansion.set` method.

        - If using the :func:`~libcasm.clexulator.ClusterExpansion.set` method, the :class:`~libcasm.clexulator.ConfigDoFValues` must be constructed consistent with the :class:`~libcasm.clexulator.SuperNeighborList`.
        - Once set by either method, ClusterExpansion maintains a non-owning pointer to that :class:`~libcasm.clexulator.ConfigDoFValues` instance.
        - The :class:`~libcasm.clexulator.ConfigDoFValues` can then be modified externally and subsequent calls of ClusterExpansion methods will use the current DoF values.

      )pbdoc")
      .def(py::init<>(&make_cluster_expansion), R"pbdoc(
          Construct a ClusterExpansion

          Parameters
          ----------
          supercell_neighbor_list: :class:`~libcasm.clexulator.SuperNeighborList`
              The :class:`~libcasm.clexulator.SuperNeighborList` for the supercell consistent with `config_dof_values`.
          clexulator: :class:`~libcasm.clexulator.Clexulator`
              The :class:`~libcasm.clexulator.Clexulator` used to evaluate basis functions
          coefficients: SparseCoefficients
              Cluster expansions coefficients used to evaluate the cluster expansion. An internal :class:`~libcasm.clexulator.Correlations` calculator is set to only evaluate the cluster basis functions with non-zero coefficients.
          config_dof_values: :class:`~libcasm.clexulator.ConfigDoFValues`
              Configuration degree of freedom (DoF) values input to the basis functions. The ClusterExpansion instance stores a pointer to the underlying data, which must have a lifetime as long as ClusterExpansion is used to calculate with its data.
          )pbdoc",
           py::arg("supercell_neighbor_list"), py::arg("clexulator"),
           py::arg("coefficients"), py::arg("config_dof_values"))
      .def("set", &clexulator::ClusterExpansion::set, R"pbdoc(
          Set the :class:`~libcasm.clexulator.ConfigDoFValues` instance ClusterExpansion uses to calculate the cluster expansion value. ClusterExpansion maintains a pointer to the underlying data, which must have a lifetime as long as ClusterExpansion is used to calculate with its data.
          )pbdoc")
      .def("intensive_value", &clexulator::ClusterExpansion::intensive_value,
           R"pbdoc(
          float: Calculate the cluster expansion value per unit cell
          )pbdoc")
      .def("extensive_value", &clexulator::ClusterExpansion::extensive_value,
           R"pbdoc(
          float: Calculate the cluster expansion value
          )pbdoc")
      .def(
          "occ_delta_value",
          [](clexulator::ClusterExpansion &x, Index linear_site_index,
             int new_occ) {
            return x.occ_delta_value(linear_site_index, new_occ);
          },
          R"pbdoc(
          Calculate the change in cluster expansion value due to a change in an occupant DoF value

          Parameters
          ----------
          linear_site_index: int
              Linear site index where an occupant DoF value is changed.
          new_occ: int
             The value the occupant DoF is changed to.
          )pbdoc",
          py::arg("linear_site_index"), py::arg("new_occ"))
      .def(
          "multi_occ_delta_value",
          [](clexulator::ClusterExpansion &x,
             std::vector<Index> const &linear_site_index,
             std::vector<int> const &new_occ) {
            return x.occ_delta_value(linear_site_index, new_occ);
          },
          R"pbdoc(
          Calculate the change in cluster expansion value due to a change in multiple occupant DoF values

          Parameters
          ----------
          key: str
              The type of local DoF that is changed.
          linear_site_index: list[int]
              Linear site indices where occupant DoF values are changed.
          new_occ: list[int]
             The value the occupant DoF are changed to.
          )pbdoc",
          py::arg("linear_site_index"), py::arg("new_occ"))
      .def("local_delta_value",
           &clexulator::ClusterExpansion::local_delta_value, R"pbdoc(
          Calculate the change in cluster expansion value due to a change in a local DoF value

          Parameters
          ----------
          key: str
              The type of local DoF that is changed.
          linear_site_index: int
              Linear site index where a local DoF value is changed.
          new_value: array_like
             The value the local DoF is changed to, in the prim basis.
          )pbdoc",
           py::arg("key"), py::arg("linear_site_index"), py::arg("new_value"))
      .def("global_delta_value",
           &clexulator::ClusterExpansion::global_delta_value, R"pbdoc(
          Calculate the change in cluster expansion value due to a change in a global DoF value

          Parameters
          ----------
          key: str
              The type of global DoF that is changed.
          new_value: array_like
             The value the global DoF is changed to, in the prim basis.
          )pbdoc",
           py::arg("key"), py::arg("new_value"))
      .def(
          "correlations",
          [](clexulator::ClusterExpansion &x) -> clexulator::Correlations & {
            return x.correlations();
          },
          py::return_value_policy::reference_internal, R"pbdoc(
          The :class:`~libcasm.clexulator.Correlations` used internally to calculate correlations, as a reference.
          )pbdoc")
      .def(
          "coefficients",
          [](clexulator::ClusterExpansion &x)
              -> clexulator::SparseCoefficients & { return x.coefficients(); },
          py::return_value_policy::reference_internal, R"pbdoc(
          The :class:`~libcasm.clexulator.SparseCoefficients` used internally to calculate the cluster expansion value, as a reference.
          )pbdoc")
      .def("required_update_neighborhood",
           &clexulator::ClusterExpansion::required_update_neighborhood, R"pbdoc(
         The coordinates of sites (relative to the origin unit cell) where a change in DoF values requires this calculator's values to be re-calculated.
         )pbdoc");

  py::class_<clexulator::MultiClusterExpansion,
             std::shared_ptr<clexulator::MultiClusterExpansion>>(
      m, "MultiClusterExpansion", R"pbdoc(
      A cluster expansion calculator

      MultiClusterExpansion is similar to :class:`~libcasm.clexulator.ClusterExpansion`, but includes multiple :class:`~libcasm.clexulator.SparseCoefficients`. When multiple cluster expansions use the same basis set, it can be used to simplify evaluating them all with a single evaluation of the basis functions.

      )pbdoc")
      .def(py::init<>(&make_multi_cluster_expansion), R"pbdoc(
          Construct a MultiClusterExpansion

          Parameters
          ----------
          supercell_neighbor_list: :class:`~libcasm.clexulator.SuperNeighborList`
              The :class:`~libcasm.clexulator.SuperNeighborList` for the supercell consistent with `config_dof_values`.
          clexulator: :class:`~libcasm.clexulator.Clexulator`
              The :class:`~libcasm.clexulator.Clexulator` used to evaluate basis functions
          coefficients: list[SparseCoefficients]
              Cluster expansions coefficients used to evaluate the cluster expansions. An internal :class:`~libcasm.clexulator.Correlations` calculator is set to only evaluate the cluster basis functions corresponding to at least one non-zero coefficient.
          config_dof_values: :class:`~libcasm.clexulator.ConfigDoFValues`
              Configuration degree of freedom (DoF) values input to the basis functions. The MultiClusterExpansion instance stores a pointer to the underlying data, which must have a lifetime as long as MultiClusterExpansion is used to calculate with its data.
          )pbdoc",
           py::arg("supercell_neighbor_list"), py::arg("clexulator"),
           py::arg("coefficients"), py::arg("config_dof_values"))
      .def("set", &clexulator::MultiClusterExpansion::set, R"pbdoc(
          Set the :class:`~libcasm.clexulator.ConfigDoFValues` instance ClusterExpansion uses to calculate the cluster expansion value. ClusterExpansion maintains a pointer to the underlying data, which must have a lifetime as long as ClusterExpansion is used to calculate with its data.
          )pbdoc")
      .def("intensive_value",
           &clexulator::MultiClusterExpansion::intensive_value, R"pbdoc(
          Calculate the cluster expansion values per unit cell

          Returns
          -------
          value : np.ndarray
              Cluster expansion values, per unit cell, as a const reference. The i-th element is the value of the i-th cluster expansion. Referred to values remain fixed until the next time a calculator function is called.
          )pbdoc")
      .def("extensive_value",
           &clexulator::MultiClusterExpansion::extensive_value, R"pbdoc(
          Calculate the cluster expansion values

          Returns
          -------
          value : np.ndarray
              Cluster expansion values, as a const reference. The i-th element is the value of the i-th cluster expansion. Referred to values remain fixed until the next time a calculator function is called.
          )pbdoc")
      .def(
          "occ_delta_value",
          [](clexulator::MultiClusterExpansion &x, Index linear_site_index,
             int new_occ) -> Eigen::VectorXd const & {
            return x.occ_delta_value(linear_site_index, new_occ);
          },
          py::return_value_policy::reference_internal, R"pbdoc(
          Calculate the change in cluster expansion values due to a change in an occupant DoF value

          Parameters
          ----------
          linear_site_index: int
              Linear site index where an occupant DoF value is changed.
          new_occ: int
             The value the occupant DoF is changed to.

          Returns
          -------
          delta_value : np.ndarray
              Change in cluster expansion values, as a const reference. The i-th element is the change in the i-th cluster expansion. Referred to values remain fixed until the next time a calculator function is called.
          )pbdoc",
          py::arg("linear_site_index"), py::arg("new_occ"))
      .def(
          "multi_occ_delta_value",
          [](clexulator::MultiClusterExpansion &x,
             std::vector<Index> const &linear_site_index,
             std::vector<int> const &new_occ) -> Eigen::VectorXd const & {
            return x.occ_delta_value(linear_site_index, new_occ);
          },
          py::return_value_policy::reference_internal, R"pbdoc(
          Calculate the change in cluster expansion values due to a change in multiple occupant DoF values

          Parameters
          ----------
          key: str
              The type of local DoF that is changed.
          linear_site_index: list[int]
              Linear site indices where occupant DoF values are changed.
          new_occ: list[int]
             The value the occupant DoF are changed to.

          Returns
          -------
          delta_value : np.ndarray
              Change in cluster expansion values, as a const reference. The i-th element is the change in the i-th cluster expansion. Referred to values remain fixed until the next time a calculator function is called.
          )pbdoc",
          py::arg("linear_site_index"), py::arg("new_occ"))
      .def("local_delta_value",
           &clexulator::MultiClusterExpansion::local_delta_value,
           py::return_value_policy::reference_internal, R"pbdoc(
          Calculate the change in cluster expansion values due to a change in a local DoF value

          Parameters
          ----------
          key: str
              The type of local DoF that is changed.
          linear_site_index: int
              Linear site index where a local DoF value is changed.
          new_value: array_like
             The value the local DoF is changed to, in the prim basis.

          Returns
          -------
          delta_value : np.ndarray
              Change in cluster expansion values, as a const reference. The i-th element is the change in the i-th cluster expansion. Referred to values remain fixed until the next time a calculator function is called.
          )pbdoc",
           py::arg("key"), py::arg("linear_site_index"), py::arg("new_value"))
      .def("global_delta_value",
           &clexulator::MultiClusterExpansion::global_delta_value,
           py::return_value_policy::reference_internal, R"pbdoc(
          Calculate the change in cluster expansion value due to a change in a global DoF value

          Parameters
          ----------
          key: str
              The type of global DoF that is changed.
          new_value: array_like
             The value the global DoF is changed to, in the prim basis.

          Returns
          -------
          delta_value : np.ndarray
              Change in cluster expansion values, as a const reference. The i-th element is the change in the i-th cluster expansion. Referred to values remain fixed until the next time a calculator function is called.
          )pbdoc",
           py::arg("key"), py::arg("new_value"))
      .def(
          "correlations",
          [](clexulator::MultiClusterExpansion &x)
              -> clexulator::Correlations & { return x.correlations(); },
          py::return_value_policy::reference_internal, R"pbdoc(
          The :class:`~libcasm.clexulator.LocalCorrelations` used internally to calculate correlations
          )pbdoc")
      .def(
          "size",
          [](clexulator::MultiClusterExpansion &x) {
            return x.coefficients().size();
          },
          py::return_value_policy::reference_internal, R"pbdoc(
          The number of cluster expansions calculated.
          )pbdoc")
      .def(
          "coefficients",
          [](clexulator::MultiClusterExpansion &x,
             int i) -> clexulator::SparseCoefficients & {
            return x.coefficients()[i];
          },
          py::return_value_policy::reference_internal, R"pbdoc(
          The :class:`~libcasm.clexulator.SparseCoefficients` used internally to calculate the i-th cluster expansion value.
          )pbdoc",
          py::arg("i"))
      .def("required_update_neighborhood",
           &clexulator::MultiClusterExpansion::required_update_neighborhood,
           R"pbdoc(
         The coordinates of sites (relative to the origin unit cell) where a change in DoF values requires this calculator's values to be re-calculated.
         )pbdoc");

  py::class_<clexulator::LocalClusterExpansion,
             std::shared_ptr<clexulator::LocalClusterExpansion>>(
      m, "LocalClusterExpansion", R"pbdoc(
      A local cluster expansion calculator

      LocalClusterExpansion is similar to :class:`~libcasm.clexulator.ClusterExpansion`, but uses a :class:`~libcasm.clexulator.LocalCorrelations` instance to calculate local cluster expansion basis functions.

      )pbdoc")
      .def(py::init<>(&make_local_cluster_expansion), R"pbdoc(
          Construct a LocalClusterExpansion

          Parameters
          ----------
          supercell_neighbor_list: :class:`~libcasm.clexulator.SuperNeighborList`
              The :class:`~libcasm.clexulator.SuperNeighborList` for the supercell consistent with `config_dof_values`.
          clexulator: :class:`~libcasm.clexulator.Clexulator`
              The :class:`~libcasm.clexulator.Clexulator` used to evaluate basis functions
          coefficients: :class:`~libcasm.clexulator.SparseCoefficients`
              Cluster expansions coefficients used to evaluate the cluster expansion. An internal :class:`~libcasm.clexulator.LocalCorrelations` calculator is set to only evaluate the cluster basis functions with non-zero coefficients.
          config_dof_values: :class:`~libcasm.clexulator.ConfigDoFValues`
              Configuration degree of freedom (DoF) values input to the basis functions. The LocalClusterExpansion instance stores a pointer to the underlying data, which must have a lifetime as long as LocalClusterExpansion is used to calculate with its data.
          )pbdoc",
           py::arg("supercell_neighbor_list"), py::arg("clexulator"),
           py::arg("coefficients"), py::arg("config_dof_values"))
      .def("set", &clexulator::LocalClusterExpansion::set, R"pbdoc(
          Set the :class:`~libcasm.clexulator.ConfigDoFValues` instance LocalClusterExpansion uses to calculate the local cluster expansion value. LocalClusterExpansion maintains a pointer to the underlying data, which must have a lifetime as long as LocalClusterExpansion is used to calculate with its data.
          )pbdoc")
      .def("value", &clexulator::LocalClusterExpansion::value, R"pbdoc(
          Calculate the local cluster expansion value

          Parameters
          ----------
          unitcell_index: int
              Linear unit cell index specifying in which unit cell to evaluate the
              local correlations.
          equivalent_index: int
              Index indicating which of the symmetrically local cluster basis sets
              to evaluate.

          Returns
          -------
          value : float
              Local cluster expansion value.
          )pbdoc",
           py::arg("unitcell_index"), py::arg("equivalent_index"))
      .def(
          "correlations",
          [](clexulator::LocalClusterExpansion &x)
              -> clexulator::LocalCorrelations & { return x.correlations(); },
          py::return_value_policy::reference_internal, R"pbdoc(
         The :class:`~libcasm.clexulator.LocalCorrelations` used internally to calculate correlations, as a reference.
         )pbdoc")
      .def(
          "coefficients",
          [](clexulator::LocalClusterExpansion &x)
              -> clexulator::SparseCoefficients & { return x.coefficients(); },
          py::return_value_policy::reference_internal, R"pbdoc(
         The list[:class:`~libcasm.clexulator.SparseCoefficients`] used internally to calculate cluster expansion values, as a reference.
         )pbdoc")
      .def("required_update_neighborhood",
           &clexulator::LocalClusterExpansion::required_update_neighborhood,
           R"pbdoc(
          The coordinates of sites (relative to the origin unit cell) where a change in DoF values requires a local cluster expansions's values to be re-calculated.

          Parameters
          ----------
          equivalent_index: int
              Index indicating which of the symmetrically local cluster basis sets to get the neighborhood for.
         )pbdoc");

  py::class_<clexulator::MultiLocalClusterExpansion,
             std::shared_ptr<clexulator::MultiLocalClusterExpansion>>(
      m, "MultiLocalClusterExpansion", R"pbdoc(
      A local cluster expansion calculator

      MultiLocalClusterExpansion is similar to :class:`~libcasm.clexulator.LocalClusterExpansion`, but includes multiple :class:`~libcasm.clexulator.SparseCoefficients`. When multiple local cluster expansions use the same basis set, it can be used to simplify evaluating them all with a single evaluation of the basis functions.

      )pbdoc")
      .def(py::init<>(&make_multi_local_cluster_expansion), R"pbdoc(
          Construct a MultiLocalClusterExpansion

          Parameters
          ----------
          supercell_neighbor_list: :class:`~libcasm.clexulator.SuperNeighborList`
              The :class:`~libcasm.clexulator.SuperNeighborList` for the supercell consistent with `config_dof_values`.
          clexulator: :class:`~libcasm.clexulator.LocalClexulator`
              The :class:`~libcasm.clexulator.LocalClexulator` used to evaluate basis functions
          coefficients: list[:class:`~libcasm.clexulator.SparseCoefficients`]
              Cluster expansions coefficients used to evaluate the cluster expansion. Internal :class:`~libcasm.clexulator.LocalCorrelations` calculators are set to only evaluate the cluster basis functions corresponding to at least one non-zero coefficient.
          config_dof_values: :class:`~libcasm.clexulator.ConfigDoFValues`
              Configuration degree of freedom (DoF) values input to the basis functions. The MultiLocalClusterExpansion instance stores a pointer to the underlying data, which must have a lifetime as long as MultiLocalClusterExpansion is used to calculate with its data.
          )pbdoc",
           py::arg("supercell_neighbor_list"), py::arg("clexulator"),
           py::arg("coefficients"), py::arg("config_dof_values"))
      .def("set", &clexulator::MultiLocalClusterExpansion::set, R"pbdoc(
          Set the :class:`~libcasm.clexulator.ConfigDoFValues` instance LocalClusterExpansion uses to calculate the local cluster expansion value. LocalClusterExpansion maintains a pointer to the underlying data, which must have a lifetime as long as LocalClusterExpansion is used to calculate with its data.
          )pbdoc")
      .def("value", &clexulator::MultiLocalClusterExpansion::values, R"pbdoc(
          Calculate the local cluster expansion value

          Parameters
          ----------
          unitcell_index: int
              Linear unit cell index specifying in which unit cell to evaluate the
              local correlations.
          equivalent_index: int
              Index indicating which of the symmetrically local cluster basis sets
              to evaluate.

          Returns
          -------
          value : np.ndarray
              Cluster expansion values, as a const reference. The i-th element is the value of the i-th cluster expansion. Referred to values remain fixed until the next time a calculator function is called.
          )pbdoc",
           py::arg("unitcell_index"), py::arg("equivalent_index"))
      .def(
          "correlations",
          [](clexulator::MultiLocalClusterExpansion &x)
              -> clexulator::LocalCorrelations & { return x.correlations(); },
          py::return_value_policy::reference_internal, R"pbdoc(
          The :class:`~libcasm.clexulator.LocalCorrelations` used internally to calculate correlations, as a reference.
          )pbdoc")
      .def(
          "size",
          [](clexulator::MultiClusterExpansion &x) {
            return x.coefficients().size();
          },
          py::return_value_policy::reference_internal, R"pbdoc(
          The number of local cluster expansions calculated.
          )pbdoc")
      .def(
          "coefficients",
          [](clexulator::MultiLocalClusterExpansion &x,
             int i) -> clexulator::SparseCoefficients & {
            return x.coefficients()[i];
          },
          py::return_value_policy::reference_internal, R"pbdoc(
          The :class:`~libcasm.clexulator.SparseCoefficients` used internally to calculate the i-th cluster expansion values, as a reference.
          )pbdoc")
      .def(
          "required_update_neighborhood",
          &clexulator::MultiLocalClusterExpansion::required_update_neighborhood,
          R"pbdoc(
          The coordinates of sites (relative to the origin unit cell) where a change in DoF values requires a local cluster expansions's values to be re-calculated.

          Parameters
          ----------
          equivalent_index: int
              Index indicating which of the symmetrically local cluster basis sets
              to get the neighborhood for.
          )pbdoc");

  // DoFSpaceAxisInfo
  py::class_<clexulator::DoFSpaceAxisInfo>(m, "DoFSpaceAxisInfo", R"pbdoc(
      DoFSpace axis glossary, axis site index, and axis dof component

      DoFSpaceAxisInfo describes the rows of a DoFSpace basis matrix.
      )pbdoc")
      .def(py::init(&make_dof_space_axis_info),
           R"pbdoc(
          Construct a DoFSpaceAxisInfo instance

          Parameters
          ----------
          dof_key: str
              A string indicating which DoF type (e.g., "disp", "Hstrain", "occ")
          xtal_prim : libcasm.xtal.Prim
              A :class:`~libcasm.xtal.Prim`
          transformation_matrix_to_super : array_like, shape=(3,3), dtype=int
              Specifies the supercell for a local DoF space. Ignored for global DoF. The transformation matrix, T, relating the superstructure lattice vectors, S, defining the DoF space to the unit structure lattice vectors, L, according to S = L @ T, where S and L are shape=(3,3) matrices with lattice vectors as columns.
          site_indices : Optional[list[int]] = None
              A set of linear index of sites in the supercell to be included in a local DoF space. Ignored for global DoF. If dof_key specifies a local DoF and this does not have a value, all sites in the supercell are included.
          )pbdoc",
           py::arg("dof_key"), py::arg("xtal_prim"),
           py::arg("transformation_matrix_to_super") = std::nullopt,
           py::arg("site_indices") = std::nullopt)
      .def_readonly("glossary", &clexulator::DoFSpaceAxisInfo::glossary,
                    R"pbdoc(
          list[str] : Names the DoF corresponding to each row of the DoFSpace basis.
          )pbdoc")
      .def_readonly("linear_site_index",
                    &clexulator::DoFSpaceAxisInfo::site_index,
                    R"pbdoc(
          Optional[list[int]] : Lookup the `linear_site_index` for each row in the DoFSpace basis.

          This has value for occupant DoF and local DoF only. It allows using the `basis_row_index` to lookup the `linear_site_index` associated with a DoFSpace basis row as follows:

          .. code-block:: Python

              linear_site_index = axis_info.linear_site_index[basis_row_index]


          )pbdoc")
      .def_readonly("dof_component_index",
                    &clexulator::DoFSpaceAxisInfo::dof_component,
                    R"pbdoc(
          Optional[list[int]] : Lookup the `dof_component_index` for each row in the DoFSpace basis.

          This has value for occupant DoF and local DoF only. It allows using the `basis_row_index` to lookup the `dof_component_index` associated with a DoFSpace basis row as follows:

          .. code-block:: Python

              dof_component_index = axis_info.dof_component_index[basis_row_index]


          - For local continuous DoF this is the index into the DoFSetBasis on the associated site.
          - For occupant DoF this gives the index into list of occupants on the associated site.

          )pbdoc")
      .def_readonly("basis_row_index",
                    &clexulator::DoFSpaceAxisInfo::basis_row_index,
                    R"pbdoc(
          Optional[list[list[int]]] : Lookup the DoFSpace basis row by `linear_site_index` and `dof_component_index`.

          This has value for occupant DoF and local DoF only. It allows using the `linear_site_index` and `dof_component_index` to lookup the corresponding DoFSpace basis row index as follows:

          .. code-block:: Python

              basis_row_index = basis_row_index[linear_site_index][dof_component_index]

          )pbdoc");

  // DoFSpace
  py::class_<clexulator::DoFSpace, std::shared_ptr<clexulator::DoFSpace>>(
      m, "DoFSpace", R"pbdoc(
      Specify a degree of freedom (DoF) space.

      A DoFSpace defines a subset of the space of allowed degrees of freedom (DoF) values.
      A choice of basis, :math:`Q`, with column basis vectors :math:`q_i`, spanning
      the space or a subspace provides a definition for order parameters, :math:`\eta`,
      according to :math:`Q \eta = x`, where :math:`x` are DoF values in the prim
      basis.
      )pbdoc")
      .def(py::init(&make_dof_space),
           R"pbdoc(
          Construct a DoFSpace

          Parameters
          ----------
          dof_key: str
              A string indicating which DoF type (e.g., "disp", "Hstrain", "occ")
          xtal_prim : libcasm.xtal.Prim
              A :class:`~libcasm.xtal.Prim`
          transformation_matrix_to_super : array_like, shape=(3,3), dtype=int
              Specifies the supercell for a local DoF space. Ignored for global DoF. The transformation matrix, T, relating the superstructure lattice vectors, S, defining the DoF space to the unit structure lattice vectors, L, according to S = L @ T, where S and L are shape=(3,3) matrices with lattice vectors as columns.
          site_indices : Optional[list[int]] = None
              A set of linear index of sites in the supercell to be included in a local DoF space. Ignored for global DoF. If dof_key specifies a local DoF and this does not have a value, all sites in the supercell are included.
          basis : Optional[array_like] = None
              The DoF space basis, :math:`Q`, with column basis vectors :math:`q_i`, spanning the space or a subspace provides a definition for order parameters, according to :math:`Q \eta = x`, where :math:`x` are DoF values in the prim basis. May be a subspace (cols <= rows). The rows of `basis` correspond to prim DoF basis axes (i.e. for local DoF a site and DoF component, or for global DoF just a DoF component). If this does not have a value, an identify matrix of appropriate dimension is used.
          )pbdoc",
           py::arg("dof_key"), py::arg("xtal_prim"),
           py::arg("transformation_matrix_to_super") = std::nullopt,
           py::arg("site_indices") = std::nullopt,
           py::arg("basis") = std::nullopt)
      .def_readonly("dof_key", &clexulator::DoFSpace::dof_key, R"pbdoc(
          str : The DoF type for this DoFSpace.
          )pbdoc")
      .def_readonly("is_global", &clexulator::DoFSpace::dof_key, R"pbdoc(
          bool : True if the DoF type is a global DoF, False otherwise.
          )pbdoc")
      .def_readonly("prim", &clexulator::DoFSpace::prim, R"pbdoc(
          ~libcasm.xtal.Prim : The prim for this DoFSpace.
          )pbdoc")
      .def_readonly("transformation_matrix_to_super",
                    &clexulator::DoFSpace::transformation_matrix_to_super,
                    R"pbdoc(
          np.ndarray : The shape=(3,3) integer matrix specifiyfing the supercell for a local DoF space.
          )pbdoc")
      .def_readonly("site_indices", &clexulator::DoFSpace::sites, R"pbdoc(
          Optional[list[int]] : The set of linear index of sites in the supercell to be included in a local DoF space.
          )pbdoc")
      .def_readonly("basis", &clexulator::DoFSpace::basis, R"pbdoc(
          np.ndarray : The DoFSpace basis, :math:`Q`.
          )pbdoc")
      .def_readonly("basis_inv", &clexulator::DoFSpace::basis_inv, R"pbdoc(
          np.ndarray : The pseudo-inverse of the DoFSpace basis.
          )pbdoc")
      .def_readonly("subspace_dim", &clexulator::DoFSpace::subspace_dim,
                    R"pbdoc(
          int : The DoF subspace dimension (equal to number of columns in basis).
          )pbdoc")
      .def_readonly("axis_info", &clexulator::DoFSpace::axis_info, R"pbdoc(
          ~libcasm.clexulator.DoFSpaceAxisInfo : Holds a description of each row of the DoFSpace basis
          )pbdoc")
      .def_static(
          "from_dict",
          [](const nlohmann::json &data,
             std::shared_ptr<xtal::BasicStructure const> const &prim)
              -> std::shared_ptr<clexulator::DoFSpace> {
            jsonParser json{data};
            InputParser<clexulator::DoFSpace> parser(json, prim);
            std::runtime_error error_if_invalid{
                "Error in libcasm.clexulator.DoFSpace.from_dict"};
            report_and_throw_if_invalid(parser, CASM::log(), error_if_invalid);
            return std::make_shared<clexulator::DoFSpace>(
                std::move(*parser.value));
          },
          R"pbdoc(
          Construct DoFSpace from a Python dict

          Parameters
          ----------
          data : dict
              The serialized OccSystem. Expected format:

                  dof: string
                      A string indicating which DoF type (e.g., "disp", "Hstrain", "occ")
                  transformation_matrix_to_supercell: Optional[list[list[float]]
                      Specifies the supercell for a local DoF space. Ignored for global DoF. The transformation matrix, T, relating the superstructure lattice vectors, S, defining the DoF space to the unit structure lattice vectors, L, according to S = L @ T, where S and L are shape=(3,3)  matrices with lattice vectors as columns.
                  sites: Optional[list[int]]
                      A set of linear index of sites in the supercell to be included in a local DoF space. Ignored for global DoF. If dof_key specifies a local DoF and this does not have a value, all sites in the supercell are included.
                  basis: list[list[float]]
                      DoFSpace basis vectors (i.e. basis[i] is the i-th column of the basis matrix :math:`Q`).

          xtal_prim : libcasm.xtal.Prim
              A :class:`~libcasm.xtal.Prim`

          Returns
          -------
          dof_space : libcasm.clexulator.DoFSpace
              The DoFSpace
          )pbdoc",
          py::arg("data"), py::arg("xtal_prim"))
      .def(
          "to_dict",
          [](clexulator::DoFSpace const &m) -> nlohmann::json {
            jsonParser json;
            to_json(m, json);
            return static_cast<nlohmann::json>(json);
          },
          "Represent the DoFSpace as a Python dict.");

  py::class_<clexulator::OrderParameter,
             std::shared_ptr<clexulator::OrderParameter>>(m, "OrderParameter",
                                                          R"pbdoc(
      An order parameter calculator

      OrderParameter calculates:

      - the value of an order parameter
      - the change in the value of an order parameter given changes in degree of freedom (DoF) values

      To calculate the order parameter value, OrderParameter uses:

      - :class:`~libcasm.clexulator.DoFSpace`: to specify the order parameter basis
      - :class:`~libcasm.xtal.SiteIndexConverter`: to perform index conversions
      - :class:`~libcasm.clexulator.ConfigDoFValues`: OrderParameter is given a pointer to a ConfigDoFValues instance and calculates the order parameters using the current state of the DoF values

      Examples
      --------

      For usage examples, see the section :ref:`Evaluating order parameters <order-parameters-index>`.

      Notes
      -----

      - An OrderParameter is set to calculate order parameters in one supercell at a time, using the appropriate :class:`~libcasm.xtal.SiteIndexConverter`. This can be set using the call operator or the :func:`~libcasm.clexulator.OrderParameter.update` method.
      - Order parameters are calculated for a :class:`~libcasm.clexulator.ConfigDoFValues` instance that can be specified using the call operator, the :func:`~libcasm.clexulator.OrderParameter.update` method, or the :func:`~libcasm.clexulator.ClusterExpansion.set` method.

        - The :class:`~libcasm.clexulator.ConfigDoFValues` must be constructed consistent with the :class:`~libcasm.xtal.SiteIndexConverter`.
        - Once set by any method, OrderParameter maintains a non-owning pointer to that :class:`~libcasm.clexulator.ConfigDoFValues` instance.
        - The :class:`~libcasm.clexulator.ConfigDoFValues` can then be modified externally and subsequent calls of OrderParameter methods will use the current DoF values.

      )pbdoc")
      .def(py::init<clexulator::DoFSpace const &>(), R"pbdoc(
          Construct an OrderParameter

          Parameters
          ----------
          dof_space: ~libcasm.clexulator.DoFSpace
              The DoFSpace defining the order parameter basis
          )pbdoc",
           py::arg("dof_space"))
      .def(
          "update",
          [](clexulator::OrderParameter &m,
             Eigen::Matrix3l const &transformation_matrix_to_super,
             xtal::UnitCellCoordIndexConverter const &supercell_index_converter,
             clexulator::ConfigDoFValues const *dof_values) {
            m.update(transformation_matrix_to_super, supercell_index_converter,
                     dof_values);
          },
          py::return_value_policy::reference,
          R"pbdoc(
          Set internal data to calculate order parameters in a particular supercell

          Parameters
          ----------
          transformation_matrix_to_super : array_like, shape=(3,3), dtype=int
              Specifies the supercell that config_dof_values is defined in.
          site_index_converter : ~libcasm.xtal.SiteIndexConverter
              Index converter for the specified supercell.
          config_dof_values: ~libcasm.clexulator.ConfigDoFValues
              The :class:`~libcasm.clexulator.ConfigDoFValues` instance OrderParameter uses to calculate the order parameter value. OrderParameter maintains a pointer to the underlying data, which must have a lifetime as long as OrderParameter is used to calculate with its data.

          )pbdoc",
          py::arg("transformation_matrix_to_super"),
          py::arg("site_index_converter"), py::arg("config_dof_values"))
      .def("set", &clexulator::OrderParameter::set, R"pbdoc(
          Set the :class:`~libcasm.clexulator.ConfigDoFValues` instance OrderParameter uses to calculate the order parameter value. OrderParameter maintains a pointer to the underlying data, which must have a lifetime as long as OrderParameter is used to calculate with its data.
          )pbdoc",
           py::arg("config_dof_values"))
      .def("value", &clexulator::OrderParameter::value,
           R"pbdoc(
          Calculate the current order parameter value

          Returns
          -------
          value : np.ndarray
              The order parameter values, as a const reference. Referred to values remain fixed until the next time a calculator function is called.
          )pbdoc")
      // occ DoF
      .def(
          "occ_delta_value",
          [](clexulator::OrderParameter &m, Index linear_site_index,
             Index new_occ) -> Eigen::VectorXd const & {
            return m.occ_delta_value(linear_site_index, new_occ);
          },
          py::return_value_policy::reference_internal,
          R"pbdoc(
          Calculate and return the change in order parameter value due to an occupation change

          Parameters
          ----------
          linear_site_index: int
              Linear site index (as defined by a :class:`~libcasm.xtal.SiteIndexConverter`) where the occupant DoF value are changed.
          new_occ: int
              The value the occupant DoF is changed to.

          Returns
          -------
          delta_value : np.ndarray
              The change in order parameter values, as a const reference. Referred to values remain fixed until the next time a calculator function is called.
          )pbdoc",
          py::arg("linear_site_index"), py::arg("new_occ"))
      .def(
          "multi_occ_delta_value",
          [](clexulator::OrderParameter &m,
             std::vector<Index> const &linear_site_index,
             std::vector<int> const &new_occ) -> Eigen::VectorXd const & {
            return m.occ_delta_value(linear_site_index, new_occ);
          },
          py::return_value_policy::reference_internal,
          R"pbdoc(
          Calculate and return the change in order parameter value due to multiple occupation changes

          Parameters
          ----------
          linear_site_index: list[int]
              Linear site indices (as defined by a :class:`~libcasm.xtal.SiteIndexConverter`) where occupant DoF values are changed.
          new_occ: list[int]
              The values the occupant DoF are changed to.

          Returns
          -------
          delta_value : np.ndarray
              The change in order parameter values, as a const reference. Referred to values remain fixed until the next time a calculator function is called.
          )pbdoc",
          py::arg("linear_site_index"), py::arg("new_occ"))
      // local DoF
      .def(
          "local_delta_value",
          [](clexulator::OrderParameter &m, Index linear_site_index,
             Eigen::VectorXd const &new_value) -> Eigen::VectorXd const & {
            return m.local_delta_value(linear_site_index, new_value);
          },
          py::return_value_policy::reference_internal,
          R"pbdoc(
          Calculate and return change in order parameter value due to a local DoF change

          Parameters
          ----------
          linear_site_index: int
              Linear site indices (as defined by a :class:`~libcasm.xtal.SiteIndexConverter`) where the local DoF value is changed.
          new_value: np.ndarray
              The value the local DoF is changed to.

          Returns
          -------
          delta_value : np.ndarray
              The change in order parameter values, as a const reference. Referred to values remain fixed until the next time a calculator function is called.
          )pbdoc",
          py::arg("linear_site_index"), py::arg("new_value"))
      .def(
          "local_component_delta_value",
          [](clexulator::OrderParameter &m, Index linear_site_index,
             Index dof_component, double new_value) -> Eigen::VectorXd const & {
            return m.local_delta_value(linear_site_index, dof_component,
                                       new_value);
          },
          py::return_value_policy::reference_internal,
          R"pbdoc(
          Calculate and return change in order parameter value due to a change in a local DoF component

          Parameters
          ----------
          linear_site_index: int
              Linear site indices (as defined by a :class:`~libcasm.xtal.SiteIndexConverter`) where the local DoF value is changed.
          dof_component: int
              Index of the the local DoF component that is changed.
          new_value: float
              The value the local DoF component is changed to.

          Returns
          -------
          delta_value : np.ndarray
              The change in order parameter values, as a const reference. Referred to values remain fixed until the next time a calculator function is called.
          )pbdoc",
          py::arg("linear_site_index"), py::arg("dof_component"),
          py::arg("new_value"))
      // global DoF
      .def(
          "global_delta_value",
          [](clexulator::OrderParameter &m,
             Eigen::VectorXd const &new_value) -> Eigen::VectorXd const & {
            return m.global_delta_value(new_value);
          },
          py::return_value_policy::reference_internal,
          R"pbdoc(
          Calculate and return change in order parameter value due to a global DoF change

          Parameters
          ----------
          new_value: np.ndarray
              The value the global DoF is changed to.

          Returns
          -------
          delta_value : np.ndarray
              The change in order parameter values, as a const reference. Referred to values remain fixed until the next time a calculator function is called.
          )pbdoc",
          py::arg("new_value"))
      .def(
          "global_component_delta_value",
          [](clexulator::OrderParameter &m, Index dof_component,
             double new_value) -> Eigen::VectorXd const & {
            return m.global_delta_value(dof_component, new_value);
          },
          py::return_value_policy::reference_internal,
          R"pbdoc(
          Calculate and return change in order parameter value due to a change in a global DoF component

          Parameters
          ----------
          dof_component: int
              Index of the the global DoF component that is changed.
          new_value: float
              The value the global DoF component is changed to.

          Returns
          -------
          delta_value : np.ndarray
              The change in order parameter values, as a const reference. Referred to values remain fixed until the next time a calculator function is called.
          )pbdoc",
          py::arg("dof_component"), py::arg("new_value"));

  //
  m.def(
      "calc_order_parameters",
      [](std::shared_ptr<clexulator::DoFSpace> const &dof_space,
         clexulator::ConfigDoFValues const &config_dof_values,
         xtal::BasicStructure const &xtal_prim,
         Eigen::Matrix3l const &transformation_matrix_to_super)
          -> Eigen::VectorXd {
        clexulator::OrderParameter f(*dof_space);
        xtal::UnitCellCoordIndexConverter index_converter(
            transformation_matrix_to_super, xtal_prim.basis().size());
        return f(transformation_matrix_to_super, index_converter,
                 &config_dof_values);
      },
      R"pbdoc(
      Calculate order parameters

      This method is safe and easy to use, but may be slower than using
      the :class:`~libcasm.clexulator.OrderParameter` class directly.

      Parameters
      ----------
      dof_space: ~libcasm.clexulator.DoFSpace
          The DoFSpace defining the order parameter basis
      config_dof_values: ConfigDoFValues
          Configuration degree of freedom (DoF) values input
      xtal_prim : libcasm.xtal.Prim
          A :class:`~libcasm.xtal.Prim`
      transformation_matrix_to_super : array_like, shape=(3,3), dtype=int
          Specifies the supercell that config_dof_values is defined in.

      Returns
      -------
      order_parameters: np.ndarray
          A vector with the calculated order parameters.

      )pbdoc",
      py::arg("dof_space"), py::arg("config_dof_values"), py::arg("xtal_prim"),
      py::arg("transformation_matrix_to_super"));

#ifdef VERSION_INFO
  m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
  m.attr("__version__") = "dev";
#endif
}
