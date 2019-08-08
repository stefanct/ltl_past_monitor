import pathlib
import pytest
import ltl_past_monitor
import debug

csv_files = pathlib.Path(__file__).parent.glob('tests/*.csv')
# Generate parameterized input including IDs with pytest >= 3.1:
# params = map(lambda p: pytest.param(p, id=p.name), csv_files)

@pytest.mark.parametrize('csv_file', csv_files)
def test_verify_csv(csv_file, pytestconfig):
  # Use pytest's verbosity
  debug.set_verbosity(pytestconfig.getoption("verbose"))

  # Try to extract the state and optional variants from the globbed CSV path
  # The variant is ignored for now
  (base, *variant, state) = str(csv_file.with_suffix('')).rsplit(sep='-', maxsplit=2)
  
  ltl_file = base + ".ltl"
  should_pass = state.startswith("pass")

  debug.vvprint("csv_file='%s', base='%s', variant='%s', state='%s', should_pass='%s', ltl_file='%s'" %
                (csv_file, base, variant, state, should_pass, ltl_file))

  ret = 1
  try:
    ret = ltl_past_monitor.verify_csv(csv_file, ltl_file)
  except SyntaxError as ex:
    assert(state == "SyntaxError")
  # else fail by passing it up automatically

  # Test return value to match should_pass
  debug.vprintn("Verification ")
  debug.vprintn("failed" if ret != 0 else "passed")
  as_intended = (ret == 0) == should_pass
  debug.vprint(" but shouldn't have!" if not as_intended else ", good.")
  assert(as_intended)
