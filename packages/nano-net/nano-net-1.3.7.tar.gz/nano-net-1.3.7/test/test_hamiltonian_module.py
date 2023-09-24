import numpy as np
import nanonet.tb as tb


def test_simple_atomic_chain():
    """ """
    site_energy = -1.0
    coupling = -1.0
    l_const = 1.0

    a = tb.Orbitals('A')
    a.add_orbital(title='s', energy=-1, )

    xyz_file = """1
    H cell
    A       0.0000000000    0.0000000000    0.0000000000
    """
    tb.set_tb_params(PARAMS_A_A={'ss_sigma': -1.0})
    h = tb.Hamiltonian(xyz=xyz_file, nn_distance=1.1)
    h.initialize()

    PRIMITIVE_CELL = [[0, 0, l_const]]
    h.set_periodic_bc(PRIMITIVE_CELL)

    num_points = 10
    kk = np.linspace(0, 3.14 / l_const, num_points, endpoint=True)

    band_structure = []

    for jj in range(num_points):
        vals, _ = h.diagonalize_periodic_bc([0.0, 0.0, kk[jj]])
        band_structure.append(vals)

    band_structure = np.array(band_structure)

    desired_value = site_energy + 2 * coupling * np.cos(l_const * kk)
    np.testing.assert_allclose(band_structure, desired_value[:, np.newaxis], atol=1e-9)


def test_atomic_chain_two_kinds_of_atoms():
    """ """
    site_energy1 = -1.0
    site_energy2 = -2.0
    coupling = -1.0
    l_const = 2.0

    a = tb.Orbitals('A')
    a.add_orbital(title='s', energy=site_energy1, )
    b = tb.Orbitals('B')
    b.add_orbital(title='s', energy=site_energy2, )

    xyz_file = """2
    H cell
    A       0.0000000000    0.0000000000    0.0000000000
    B       0.0000000000    0.0000000000    1.0000000000
    """
    tb.set_tb_params(PARAMS_A_B={'ss_sigma': coupling})
    h = tb.Hamiltonian(xyz=xyz_file, nn_distance=1.1)
    h.initialize()

    PRIMITIVE_CELL = [[0, 0, l_const]]
    h.set_periodic_bc(PRIMITIVE_CELL)

    num_points = 10
    kk = np.linspace(0, 3.14 / 2, num_points, endpoint=True)

    band_structure = []

    for jj in range(num_points):
        vals, _ = h.diagonalize_periodic_bc([0.0, 0.0, kk[jj]])
        band_structure.append(vals)

    band_structure = np.array(band_structure)
    desired_value = np.zeros(band_structure.shape)

    b = site_energy1 + site_energy2
    c = site_energy1 * site_energy2 - (2.0 * coupling * np.cos(0.5 * kk * l_const)) ** 2
    desired_value[:, 0] = 0.5 * (b - np.sqrt(b ** 2 - 4.0 * c))
    desired_value[:, 1] = 0.5 * (b + np.sqrt(b ** 2 - 4.0 * c))

    np.testing.assert_allclose(band_structure, desired_value, atol=1e-9)


def test_bulk_silicon():
    """ """
    a_si = 5.50
    PRIMITIVE_CELL = [[0, 0.5 * a_si, 0.5 * a_si],
                      [0.5 * a_si, 0, 0.5 * a_si],
                      [0.5 * a_si, 0.5 * a_si, 0]]

    tb.Orbitals.orbital_sets = {'Si': 'SiliconSP3D5S'}

    xyz_file = """2
    Si2 cell
    Si1       0.0000000000    0.0000000000    0.0000000000
    Si2       1.3750000000    1.3750000000    1.3750000000
    """

    h = tb.Hamiltonian(xyz=xyz_file, nn_distance=2.5)
    h.initialize()
    h.set_periodic_bc(PRIMITIVE_CELL)

    sym_points = ['L', 'GAMMA', 'X']
    num_points = [10, 25]
    k = tb.get_k_coords(sym_points, num_points, 'Si')
    band_sructure = []

    vals = np.zeros((sum(num_points), h.h_matrix.shape[0]), dtype=complex)

    for jj, item in enumerate(k):
        vals[jj, :], _ = h.diagonalize_periodic_bc(item)

    band_structure = np.real(np.array(vals))
    np.testing.assert_allclose(band_structure, expected_bulk_silicon_band_structure(), atol=1e-4)


def expected_bulk_silicon_band_structure():
    """ """
    return np.array([[-1.02206739e+01, -6.65655472e+00, -1.10180247e+00,
                      -1.10180247e+00, 2.14081014e+00, 4.39529148e+00,
                      4.39529148e+00, 8.97698100e+00, 8.97698100e+00,
                      9.24843628e+00, 1.37408367e+01, 1.37408367e+01,
                      1.44013317e+01, 1.70471035e+01, 1.81023949e+01,
                      1.96697163e+01, 1.96697163e+01, 2.01429770e+01,
                      2.01429770e+01, 2.87043522e+01],
                     [-1.03191648e+01, -6.48697502e+00, -1.08674150e+00,
                      -1.08674150e+00, 2.17499014e+00, 4.43846801e+00,
                      4.43846801e+00, 8.89086844e+00, 8.89086844e+00,
                      9.17376552e+00, 1.38675824e+01, 1.38675824e+01,
                      1.43178651e+01, 1.65251028e+01, 1.84287865e+01,
                      1.93860265e+01, 1.93860265e+01, 2.03277962e+01,
                      2.03277962e+01, 2.89528298e+01],
                     [-1.05715036e+01, -6.02100242e+00, -1.03903698e+00,
                      -1.03903698e+00, 2.27655847e+00, 4.54326507e+00,
                      4.54326507e+00, 8.69156023e+00, 8.69156023e+00,
                      8.94650091e+00, 1.40285746e+01, 1.42050454e+01,
                      1.42050454e+01, 1.56043230e+01, 1.88694525e+01,
                      1.88694525e+01, 1.88816261e+01, 2.05537138e+01,
                      2.05537138e+01, 2.96221229e+01],
                     [-1.08993983e+01, -5.33606230e+00, -9.52888699e-01,
                      -9.52888699e-01, 2.44199398e+00, 4.63585668e+00,
                      4.63585668e+00, 8.51949533e+00, 8.51949533e+00,
                      8.55707499e+00, 1.33646694e+01, 1.46597628e+01,
                      1.46597628e+01, 1.48263466e+01, 1.82633895e+01,
                      1.82633895e+01, 1.92686766e+01, 2.06983843e+01,
                      2.06983843e+01, 3.05438989e+01],
                     [-1.12439034e+01, -4.49073964e+00, -8.23437358e-01,
                      -8.23437358e-01, 2.66345483e+00, 4.61436032e+00,
                      4.61436032e+00, 7.99027157e+00, 8.52836710e+00,
                      8.52836710e+00, 1.23138258e+01, 1.43898069e+01,
                      1.51220515e+01, 1.51220515e+01, 1.76285580e+01,
                      1.76285580e+01, 1.95938679e+01, 2.07541005e+01,
                      2.07541005e+01, 3.15506161e+01],
                     [-1.15680147e+01, -3.52487687e+00, -6.51579679e-01,
                      -6.51579679e-01, 2.92581303e+00, 4.42293214e+00,
                      4.42293214e+00, 7.23118102e+00, 8.80140385e+00,
                      8.80140385e+00, 1.12006297e+01, 1.41249031e+01,
                      1.54086285e+01, 1.54086285e+01, 1.71136049e+01,
                      1.71136049e+01, 1.98639543e+01, 2.07290103e+01,
                      2.07290103e+01, 3.25136105e+01],
                     [-1.18464713e+01, -2.47647238e+00, -4.48752890e-01,
                      -4.48752890e-01, 3.20166018e+00, 4.10621952e+00,
                      4.10621952e+00, 6.29176815e+00, 9.30333392e+00,
                      9.30333392e+00, 1.02361074e+01, 1.39396630e+01,
                      1.51998540e+01, 1.51998540e+01, 1.70226045e+01,
                      1.70226045e+01, 2.00788230e+01, 2.06407409e+01,
                      2.06407409e+01, 3.33421219e+01],
                     [-1.20601120e+01, -1.40567122e+00, -2.42182437e-01,
                      -2.42182437e-01, 3.43967056e+00, 3.76371303e+00,
                      3.76371303e+00, 5.26309177e+00, 9.50883297e+00,
                      9.92593446e+00, 9.92593446e+00, 1.38118749e+01,
                      1.45990639e+01, 1.45990639e+01, 1.72585638e+01,
                      1.72585638e+01, 2.02355385e+01, 2.05189073e+01,
                      2.05189073e+01, 3.39739745e+01],
                     [-1.21944834e+01, -4.56462760e-01, -7.86878851e-02,
                      -7.86878851e-02, 3.49855528e+00, 3.49855528e+00,
                      3.51891013e+00, 4.40960438e+00, 9.05408948e+00,
                      1.05089642e+01, 1.05089642e+01, 1.37360519e+01,
                      1.39897300e+01, 1.39897300e+01, 1.74967642e+01,
                      1.74967642e+01, 2.03309978e+01, 2.04086742e+01,
                      2.04086742e+01, 3.43684925e+01],
                     [-1.22403411e+01, -1.47633853e-02, -1.47633853e-02,
                      -1.47633853e-02, 3.39764477e+00, 3.39764477e+00,
                      3.39764477e+00, 4.15028828e+00, 8.89794108e+00,
                      1.07761333e+01, 1.07761333e+01, 1.37108523e+01,
                      1.37108523e+01, 1.37108523e+01, 1.75910667e+01,
                      1.75910667e+01, 2.03630663e+01, 2.03630663e+01,
                      2.03630663e+01, 3.45025117e+01],
                     [-1.22403411e+01, -1.47633853e-02, -1.47633853e-02,
                      -1.47633853e-02, 3.39764477e+00, 3.39764477e+00,
                      3.39764477e+00, 4.15028828e+00, 8.89794108e+00,
                      1.07761333e+01, 1.07761333e+01, 1.37108523e+01,
                      1.37108523e+01, 1.37108523e+01, 1.75910667e+01,
                      1.75910667e+01, 2.03630663e+01, 2.03630663e+01,
                      2.03630663e+01, 3.45025117e+01],
                     [-1.22316949e+01, -5.96351084e-02, -5.09690825e-02,
                      -5.09690825e-02, 3.37993623e+00, 3.44823512e+00,
                      3.44823512e+00, 4.18662805e+00, 8.92737659e+00,
                      1.06622597e+01, 1.07834290e+01, 1.37084400e+01,
                      1.37084400e+01, 1.38316064e+01, 1.75620138e+01,
                      1.75837710e+01, 2.03510940e+01, 2.03510940e+01,
                      2.03986333e+01, 3.44772760e+01],
                     [-1.22057925e+01, -1.89135832e-01, -1.53355806e-01,
                      -1.53355806e-01, 3.32796185e+00, 3.59369606e+00,
                      3.59369606e+00, 4.28983692e+00, 9.01436685e+00,
                      1.03666392e+01, 1.08052846e+01, 1.37012503e+01,
                      1.37012503e+01, 1.41485645e+01, 1.74801143e+01,
                      1.75619154e+01, 2.03152095e+01, 2.03152095e+01,
                      2.05001610e+01, 3.44016837e+01],
                     [-1.21627406e+01, -3.90406447e-01, -3.06907054e-01,
                      -3.06907054e-01, 3.24491613e+00, 3.81877171e+00,
                      3.81877171e+00, 4.44478690e+00, 9.15519687e+00,
                      9.97078046e+00, 1.08416067e+01, 1.36894247e+01,
                      1.36894247e+01, 1.45824870e+01, 1.73583395e+01,
                      1.75255933e+01, 2.02555107e+01, 2.02555107e+01,
                      2.06549606e+01, 3.42760797e+01],
                     [-1.21027137e+01, -6.47906528e-01, -4.94726660e-01,
                      -4.94726660e-01, 3.13538981e+00, 4.10616678e+00,
                      4.10616678e+00, 4.63148985e+00, 9.34432158e+00,
                      9.53477469e+00, 1.08922397e+01, 1.36731979e+01,
                      1.36731979e+01, 1.50777308e+01, 1.72120285e+01,
                      1.74749603e+01, 2.01721620e+01, 2.01721620e+01,
                      2.08482483e+01, 3.41010368e+01],
                     [-1.20259480e+01, -9.47300852e-01, -7.02476118e-01,
                      -7.02476118e-01, 3.00462077e+00, 4.44098324e+00,
                      4.44098324e+00, 4.82776187e+00, 9.09727108e+00,
                      9.57497572e+00, 1.09569668e+01, 1.36528965e+01,
                      1.36528965e+01, 1.56034954e+01, 1.70553716e+01,
                      1.74102332e+01, 2.00653964e+01, 2.00653964e+01,
                      2.10667986e+01, 3.38773539e+01],
                     [-1.19327347e+01, -1.27701013e+00, -9.19499514e-01,
                      -9.19499514e-01, 2.85788599e+00, 4.81184396e+00,
                      4.81184396e+00, 5.00870822e+00, 8.68862989e+00,
                      9.83957052e+00, 1.10355109e+01, 1.36289368e+01,
                      1.36289368e+01, 1.61427357e+01, 1.69005250e+01,
                      1.73316891e+01, 1.99355187e+01, 1.99355187e+01,
                      2.13000367e+01, 3.36060528e+01],
                     [-1.18234115e+01, -1.62824206e+00, -1.13832128e+00,
                      -1.13832128e+00, 2.70013130e+00, 5.14423759e+00,
                      5.21038780e+00, 5.21038780e+00, 8.34035986e+00,
                      1.01297695e+01, 1.11275354e+01, 1.36018238e+01,
                      1.36018238e+01, 1.66852409e+01, 1.67581480e+01,
                      1.72396646e+01, 1.97829096e+01, 1.97829096e+01,
                      2.15397921e+01, 3.32883743e+01],
                     [-1.16983534e+01, -1.99446562e+00, -1.35379667e+00,
                      -1.35379667e+00, 2.53581459e+00, 5.19890419e+00,
                      5.63041506e+00, 5.63041506e+00, 8.08810334e+00,
                      1.04362692e+01, 1.12326466e+01, 1.35721500e+01,
                      1.35721500e+01, 1.66383623e+01, 1.71345534e+01,
                      1.72242810e+01, 1.96080317e+01, 1.96080317e+01,
                      2.17797114e+01, 3.29257729e+01],
                     [-1.15579633e+01, -2.37083034e+00, -1.56238986e+00,
                      -1.56238986e+00, 2.36888959e+00, 5.14263206e+00,
                      6.06715690e+00, 6.06715690e+00, 7.96192597e+00,
                      1.07484038e+01, 1.13503941e+01, 1.35405957e+01,
                      1.35405957e+01, 1.65516864e+01, 1.70168059e+01,
                      1.77550112e+01, 1.94114373e+01, 1.94114373e+01,
                      2.20147324e+01, 3.25199121e+01],
                     [-1.14026633e+01, -2.75369436e+00, -1.76165882e+00,
                      -1.76165882e+00, 2.20286077e+00, 4.97139081e+00,
                      6.51674559e+00, 6.51674559e+00, 7.96595712e+00,
                      1.10537891e+01, 1.14802738e+01, 1.35079333e+01,
                      1.35079333e+01, 1.65097159e+01, 1.68869262e+01,
                      1.82736833e+01, 1.91937799e+01, 1.91937799e+01,
                      2.22407031e+01, 3.20726575e+01],
                     [-1.12328863e+01, -3.14027951e+00, -1.94990911e+00,
                      -1.94990911e+00, 2.04086174e+00, 4.71116732e+00,
                      6.97584428e+00, 6.97584428e+00, 8.07448223e+00,
                      1.13383796e+01, 1.16217296e+01, 1.34750355e+01,
                      1.34750355e+01, 1.65252429e+01, 1.67454704e+01,
                      1.87772352e+01, 1.89558293e+01, 1.89558293e+01,
                      2.24541264e+01, 3.15860704e+01],
                     [-1.10490690e+01, -3.52842883e+00, -2.12596440e+00,
                      -2.12596440e+00, 1.88573127e+00, 4.39753038e+00,
                      7.44137893e+00, 7.44137893e+00, 8.25235743e+00,
                      1.15874534e+01, 1.17741556e+01, 1.34428923e+01,
                      1.34428923e+01, 1.65930444e+01, 1.66113631e+01,
                      1.86984931e+01, 1.86984931e+01, 1.92630675e+01,
                      2.26519941e+01, 3.10624007e+01],
                     [-1.08516462e+01, -3.91643733e+00, -2.28901327e+00,
                      -2.28901327e+00, 1.74007561e+00, 4.05915445e+00,
                      7.91032348e+00, 7.91032348e+00, 8.47144106e+00,
                      1.17878478e+01, 1.19368993e+01, 1.34126413e+01,
                      1.34126413e+01, 1.64303007e+01, 1.67792888e+01,
                      1.84228485e+01, 1.84228485e+01, 1.97289169e+01,
                      2.28316797e+01, 3.05040792e+01],
                     [-1.06410474e+01, -4.30293282e+00, -2.43850513e+00,
                      -2.43850513e+00, 1.60631404e+00, 3.71510690e+00,
                      8.37949762e+00, 8.37949762e+00, 8.71325830e+00,
                      1.19308798e+01, 1.21092636e+01, 1.33856187e+01,
                      1.33856187e+01, 1.62579364e+01, 1.70354583e+01,
                      1.81301888e+01, 1.81301888e+01, 2.01727824e+01,
                      2.29908698e+01, 2.99137107e+01],
                     [-1.04176940e+01, -4.68679042e+00, -2.57407755e+00,
                      -2.57407755e+00, 1.48670883e+00, 3.37747294e+00,
                      8.84533839e+00, 8.84533839e+00, 8.96633099e+00,
                      1.20142975e+01, 1.22905106e+01, 1.33634436e+01,
                      1.33634436e+01, 1.60766894e+01, 1.73796073e+01,
                      1.78220955e+01, 1.78220955e+01, 2.05928800e+01,
                      2.31275195e+01, 2.92940673e+01],
                     [-1.01819988e+01, -5.06706982e+00, -2.69550423e+00,
                      -2.69550423e+00, 1.38338235e+00, 3.05401292e+00,
                      9.22347934e+00, 9.30360221e+00, 9.30360221e+00,
                      1.20418618e+01, 1.24798641e+01, 1.33481506e+01,
                      1.33481506e+01, 1.58873359e+01, 1.75005514e+01,
                      1.75005514e+01, 1.78052087e+01, 2.09876157e+01,
                      2.32398253e+01, 2.86480826e+01],
                     [-9.93436682e+00, -5.44296849e+00, -2.80265664e+00,
                      -2.80265664e+00, 1.29832399e+00, 2.74986894e+00,
                      9.48007773e+00, 9.74894442e+00, 9.74894442e+00,
                      1.20209775e+01, 1.26765132e+01, 1.33423846e+01,
                      1.33423846e+01, 1.56906868e+01, 1.71681276e+01,
                      1.71681276e+01, 1.83018647e+01, 2.13555662e+01,
                      2.33262073e+01, 2.79788489e+01],
                     [-9.67519699e+00, -5.81378612e+00, -2.89547492e+00,
                      -2.89547492e+00, 1.23338981e+00, 2.46854736e+00,
                      9.73303747e+00, 1.01743250e+01, 1.01743250e+01,
                      1.19600479e+01, 1.28796158e+01, 1.33496463e+01,
                      1.33496463e+01, 1.54875842e+01, 1.68283036e+01,
                      1.68283036e+01, 1.88579746e+01, 2.16954633e+01,
                      2.33853027e+01, 2.72896201e+01],
                     [-9.40488466e+00, -6.17889778e+00, -2.97394546e+00,
                      -2.97394546e+00, 1.19029672e+00, 2.21247466e+00,
                      9.98021761e+00, 1.05702490e+01, 1.05702490e+01,
                      1.18667356e+01, 1.30883023e+01, 1.33744520e+01,
                      1.33744520e+01, 1.52788977e+01, 1.64860445e+01,
                      1.64860445e+01, 1.94624924e+01, 2.20061728e+01,
                      2.34159678e+01, 2.65838249e+01],
                     [-9.12382463e+00, -6.53773361e+00, -3.03808323e+00,
                      -3.03808323e+00, 1.17061306e+00, 1.98331708e+00,
                      1.02200719e+01, 1.09240949e+01, 1.09240949e+01,
                      1.17472603e+01, 1.33016791e+01, 1.34218918e+01,
                      1.34218918e+01, 1.50655209e+01, 1.61488965e+01,
                      1.61488965e+01, 2.01056342e+01, 2.22866514e+01,
                      2.34173001e+01, 2.58651102e+01],
                     [-8.83241413e+00, -6.88976404e+00, -3.08791798e+00,
                      -3.08791798e+00, 1.17574622e+00, 1.78217048e+00,
                      1.04514236e+01, 1.12203608e+01, 1.12203608e+01,
                      1.16063501e+01, 1.34951986e+01, 1.34951986e+01,
                      1.35188324e+01, 1.48483676e+01, 1.58291586e+01,
                      1.58291586e+01, 2.07788802e+01, 2.25358146e+01,
                      2.33887137e+01, 2.51374792e+01],
                     [-8.53105566e+00, -7.23448919e+00, -3.12348347e+00,
                      -3.12348347e+00, 1.20692827e+00, 1.60967772e+00,
                      1.06733083e+01, 1.14431112e+01, 1.14431112e+01,
                      1.14474732e+01, 1.35890120e+01, 1.35890120e+01,
                      1.37388322e+01, 1.46283678e+01, 1.55481602e+01,
                      1.55481602e+01, 2.14744857e+01, 2.27519760e+01,
                      2.33302286e+01, 2.44058670e+01],
                     [-8.22015947e+00, -7.57143176e+00, -3.14480944e+00,
                      -3.14480944e+00, 1.26519956e+00, 1.46610500e+00,
                      1.08848485e+01, 1.12731345e+01, 1.15803570e+01,
                      1.15803570e+01, 1.36783654e+01, 1.36783654e+01,
                      1.39607367e+01, 1.44064633e+01, 1.53428871e+01,
                      1.53428871e+01, 2.21835245e+01, 2.29283290e+01,
                      2.32441642e+01, 2.36806861e+01],
                     [-7.90014554e+00, -7.90013239e+00, -3.15191594e+00,
                      -3.15191594e+00, 1.35139035e+00, 1.35139441e+00,
                      1.10851394e+01, 1.10851473e+01, 1.16265064e+01,
                      1.16265064e+01, 1.37174715e+01, 1.37174715e+01,
                      1.41835955e+01, 1.41836045e+01, 1.52647380e+01,
                      1.52647380e+01, 2.28624963e+01, 2.28625186e+01,
                      2.31682950e+01, 2.31682966e+01]])


if __name__ == '__main__':
    # test_simple_atomic_chain()
    test_atomic_chain_two_kinds_of_atoms()
    # test_bulk_silicon()
