from generate import * 

def test_slashes():
    assert reformat_label("SDA/PB2") == "SDA / PB2"
    assert reformat_label("SDA/PB2/MISO") == "SDA / PB2 / MISO"
    # Already have spaces -> unchanged
    assert reformat_label("SDA / PB2 / MISO") == "SDA / PB2 / MISO"

def test_inverted_pins():
    assert reformat_label('~{RESET}') == 'RESET (active low)'
    assert reformat_label('A B ~{RESET} C') == 'A B RESET (active low) C'
    assert reformat_label('~{ONE} ~{TWO}') == 'ONE (active low) TWO (active low)'

def test_subscript():
    assert reformat_label('V_{cc}') == 'V_cc'
    assert reformat_label('V_{cc} V_{dd}') == 'V_cc V_dd'

def test_superscript():
    assert reformat_label('V^{+}') == 'V_+'
    assert reformat_label('V^{+} V^{a}') == 'V_+ V_a'

