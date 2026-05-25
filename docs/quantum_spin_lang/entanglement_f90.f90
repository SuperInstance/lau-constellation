! entanglement_f90.f90 — Entanglement = Consonance (Fortran 90)
!
! Physics Analogy:
!   Two coupled oscillators (musical modes) with coupling g.
!   Hamiltonian: H = w1*s1+s1- + w2*s2+s2- + g*(s1+s2- + s1-s2+)
!   Evolve |10> state. In the {|01>,|10>} subspace, this is a 2-level system
!   with detuning delta = w2-w1 and Rabi frequency Omega = sqrt(delta^2 + 4g^2).
!   Exact solution gives entanglement via von Neumann entropy.
!
! Compile: gfortran -O2 -o entanglement_f90 entanglement_f90.f90

program entanglement_consonance
  implicit none
  integer, parameter :: N_INT = 13
  double precision :: w1, w2, g, t_evolve
  double precision :: delta_val, omega_r
  double precision :: c10_re, c10_im, c01_re, c01_im
  double precision :: p10, p01, S, tenney, cents_val
  character(len=10) :: names(N_INT)
  double precision :: ratios(N_INT)
  integer :: k

  names = (/ "Unison ", "m2     ", "M2     ", "m3     ", "M3     ", &
             "P4     ", "TT     ", "P5     ", "m6     ", "M6     ", &
             "m7     ", "M7     ", "Octave " /)
  ratios = (/ 1.0d0, 16.0d0/15.0d0, 9.0d0/8.0d0, 6.0d0/5.0d0, 5.0d0/4.0d0, &
              4.0d0/3.0d0, 45.0d0/32.0d0, 3.0d0/2.0d0, 8.0d0/5.0d0, &
              5.0d0/3.0d0, 9.0d0/5.0d0, 15.0d0/8.0d0, 2.0d0 /)

  w1 = 1.0d0
  g = 0.5d0
  t_evolve = 1.0d0

  write(*, '(A)') '{"experiment": "entanglement_consonance",'
  write(*, '(A)') ' "language": "Fortran 90",'
  write(*, '(A)') ' "description": "Correlate von Neumann entropy with Tenney height",'
  write(*, '(A,F5.2,A,F5.2,A)') ' "parameters": {"coupling_g":', g, ', "evolution_time":', t_evolve, '},'
  write(*, '(A)') ' "results": ['

  do k = 1, N_INT
    w2 = ratios(k)

    ! Detuning and Rabi frequency for the {|01>,|10>} subspace
    ! Exact 2-level solution:
    !   delta = w2 - w1, Omega_R = sqrt(delta^2 + 4*g^2)
    !   |psi(t)> = [cos(Ot/2) + i*(delta/Omega)*sin(Ot/2)] |10>
    !             + [-i*(2g/Omega)*sin(Ot/2)] |01>
    delta_val = w2 - w1
    omega_r = sqrt(delta_val**2 + 4.0d0 * g**2)

    c10_re = cos(omega_r * t_evolve / 2.0d0)
    c10_im = (delta_val / omega_r) * sin(omega_r * t_evolve / 2.0d0)
    c01_re = 0.0d0
    c01_im = -(2.0d0 * g / omega_r) * sin(omega_r * t_evolve / 2.0d0)

    ! Probabilities = squared amplitudes
    p10 = c10_re**2 + c10_im**2
    p01 = c01_re**2 + c01_im**2

    ! Von Neumann entropy: S = -sum lambda_i * log2(lambda_i)
    ! Reduced density matrix is diagonal with eigenvalues p01 and p10
    S = 0.0d0
    if (p01 > 1.0d-12) S = S - p01 * log(p01) / log(2.0d0)
    if (p10 > 1.0d-12) S = S - p10 * log(p10) / log(2.0d0)

    tenney = log(max(w2, 1.0d0/w2)) / log(2.0d0)
    cents_val = 1200.0d0 * log(w2) / log(2.0d0)

    if (k < N_INT) then
      write(*, '(A,A10,A,F10.8,A,F10.4,A,F12.8,A,F8.6,A,F8.6,A)') &
        '  {"name": "', trim(names(k)), '", "ratio":', w2, &
        ', "cents":', cents_val, ', "entanglement_entropy":', S, &
        ', "eigenvalues": [', p01, ',', p10, ']},'
    else
      write(*, '(A,A10,A,F10.8,A,F10.4,A,F12.8,A,F8.6,A,F8.6,A)') &
        '  {"name": "', trim(names(k)), '", "ratio":', w2, &
        ', "cents":', cents_val, ', "entanglement_entropy":', S, &
        ', "eigenvalues": [', p01, ',', p10, ']}'
    end if
  end do

  write(*, '(A)') ' ],'
  write(*, '(A)') ' "physics_interpretation": "Detuned coupling produces Rabi '&
    //'oscillations; entanglement entropy quantifies quantum coherence."'
  write(*, '(A)') '}'

end program entanglement_consonance
