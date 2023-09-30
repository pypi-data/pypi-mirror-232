// Note:
// - Requires environment variable CASM_PREFIX to specify `global` and
// `crystallography` CASM libraries install location
//   - CASM_PREFIX is recognized by
//   `RuntimeLibrary::default_casm_includedir()`
//     and `RuntimeLibrary::default_casm_libdir()`
//

#include "casm/clexulator/io/json/Clexulator_json_io.hh"

#include "TestClexulatorBase.hh"
#include "TestLocalClexulatorBase.hh"
#include "casm/casm_io/json/InputParser_impl.hh"
#include "casm/clexulator/Clexulator.hh"

using namespace CASM;

// Test using data/OccClexulatorFCCTernaryTest, which is currently
// generated as part of the OccClexulatorFCCTest in the main CASMcode repo
//
class OccClexulatorFCCTernaryJsonIOTest : public test::TestClexulatorBase {
 protected:
  OccClexulatorFCCTernaryJsonIOTest()
      : TestClexulatorBase("OccClexulatorTest_Clexulator", "default",
                           "OccClexulatorFCCTernaryTest", true) {}
};

TEST_F(OccClexulatorFCCTernaryJsonIOTest, Test1) {
  std::string src_filename = clexulator_name + ".cc";

  fs::copy_file(
      test_data_dir / "basis_sets" / ("bset." + bset_name) / src_filename,
      tmpdir.path() / src_filename);

  jsonParser json;
  json["source"] = (tmpdir.path() / src_filename).string();
  json["compile_options"] = compile_opt;
  json["so_options"] = so_opt;

  InputParser<clexulator::Clexulator> parser(json, prim_neighbor_list);
  EXPECT_EQ(parser.valid(), true);

  // Check constructed clexulator
  auto &clexulator = parser.value;
  EXPECT_EQ(clexulator->name(), clexulator_name);
  EXPECT_EQ(clexulator->nlist_size(), 176);
  EXPECT_EQ(clexulator->corr_size(), 75);
  EXPECT_EQ(clexulator->n_point_corr(), 1);
  EXPECT_EQ(clexulator->neighborhood().size(), 75);
}

class LocalOccClexulatorZrOJsonIOTest : public test::TestLocalClexulatorBase {
 protected:
  LocalOccClexulatorZrOJsonIOTest()
      : TestLocalClexulatorBase("LocalOccClexulatorZrOTest_Clexulator",
                                {"hop0", "hop1"}, "LocalOccClexulatorZrOTest",
                                true) {}
};

TEST_F(LocalOccClexulatorZrOJsonIOTest, Test1) {
  // copy files to tmpdir for use
  for (std::string const &bset_name : bset_names) {
    copy_local_clexulator(test_data_dir / "basis_sets",
                          tmpdir.path() / "basis_sets", bset_name,
                          clexulator_basename);
  }

  // make Clexulator
  for (std::string const &bset_name : bset_names) {
    jsonParser json;
    fs::path source = tmpdir.path() / "basis_sets" / ("bset." + bset_name) /
                      (clexulator_basename + "_" + bset_name + ".cc");
    json["source"] = source.string();
    json["compile_options"] = compile_opt;
    json["so_options"] = so_opt;

    InputParser<std::vector<clexulator::Clexulator>> parser(json,
                                                            prim_neighbor_list);
    EXPECT_EQ(parser.valid(), true);

    // loop over clexulator for equivalent phenomenal clusters
    Index i = 0;
    for (auto &equiv_clexulator : *parser.value) {
      EXPECT_EQ(equiv_clexulator.name(), clexulator_basename + "_" + bset_name +
                                             "_" + std::to_string(i));
      EXPECT_EQ(equiv_clexulator.nlist_size(), 53);
      EXPECT_EQ(equiv_clexulator.corr_size(), 33);
      EXPECT_EQ(equiv_clexulator.n_point_corr(), 53);
      EXPECT_EQ(equiv_clexulator.neighborhood().size(), 26);
      ++i;
    }
  }
}
