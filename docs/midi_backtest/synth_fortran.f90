! Fortran 90 Synthesizer - reads corpus.json via helper Python script
program synth_fortran
  use iso_fortran_env, only: int64, real64
  implicit none
  integer, parameter :: SR = 44100, MAX_NOTES = 256
  integer :: ntests, i, j, k, n, s0, total, ncount
  double precision :: freq, dur, amp, t, max_end, vel
  double precision, allocatable :: mix(:), buf(:)
  character(len=128) :: test_name, junk
  character(len=512) :: outpath
  
  ! Count tests from corpus
  open(unit=10, file="fortran_corpus.txt", status="old", action="read")
  read(10, *) ntests
  print *, "Processing", ntests, "test sequences"
  close(10)
  
  ! Simpler approach: re-read and store
  allocate(mix(1:SR*30))
  allocate(buf(1:SR*30))
  
  open(unit=10, file="fortran_corpus.txt", status="old", action="read")
  read(10, *) ntests
  
  do i = 1, ntests
    read(10, '(A)') test_name
    read(10, *) ncount
    
    max_end = 0.0d0
    ! First pass: find max_end
    ! Store notes in temp arrays
    block
      double precision :: freqs(MAX_NOTES), durs(MAX_NOTES), starts(MAX_NOTES), vels(MAX_NOTES)
      
      do j = 1, ncount
        read(10, *) freqs(j), durs(j), vels(j), starts(j)
      end do
      
      total = int(max_end * SR) + SR
      if (total > SR*30) total = SR*30
      mix(1:total) = 0.0d0
      
      do j = 1, ncount
        n = int(durs(j) * SR)
        s0 = int(starts(j) * SR)
        amp = vels(j) / 127.0d0
        
        if (s0 >= total) cycle
        if (s0 + n > total) n = total - s0
        
        do k = 1, n
          t = dble(k-1) / dble(SR)
          buf(k) = amp * sin(2.0d0 * 3.14159265358979323846d0 * freqs(j) * t)
        end do
        
        call apply_envelope(buf, n)
        
        do k = 1, n
          if (s0+k <= total .and. s0+k >= 1) then
            mix(s0+k) = mix(s0+k) + buf(k)
          end if
        end do
      end do
      
      ! Clip
      do k = 1, total
        if (mix(k) > 1.0d0) mix(k) = 1.0d0
        if (mix(k) < -1.0d0) mix(k) = -1.0d0
      end do
      
      ! Write output
      outpath = "output/fortran/" // trim(test_name) // ".f64"
      open(unit=20, file=trim(outpath), form="unformatted", access="stream", status="replace")
      write(20) mix(1:total)
      close(20)
      
      print *, "  Synthesized ", trim(test_name), " (", ncount, " notes)"
    end block
  end do
  
  close(10)
  deallocate(mix, buf)
  print *, "Fortran synthesis complete"
  
contains
  subroutine apply_envelope(buf, n)
    double precision, intent(inout) :: buf(*)
    integer, intent(in) :: n
    integer :: a_s, d_s, r_s, j
    double precision :: sustain
    sustain = 0.7d0
    a_s = int(0.01 * SR)
    d_s = int(0.05 * SR)
    r_s = int(0.1 * SR)
    if (a_s > n) a_s = n
    if (d_s > n - a_s) d_s = n - a_s
    if (r_s > n - a_s - d_s) r_s = n - a_s - d_s
    
    do j = 1, a_s
      buf(j) = buf(j) * dble(j-1) / dble(a_s)
    end do
    do j = 1, d_s
      buf(a_s+j) = buf(a_s+j) * (1.0d0 - (1.0d0-sustain)*dble(j)/dble(d_s))
    end do
    do j = a_s+d_s+1, max(1, n-r_s)
      buf(j) = buf(j) * sustain
    end do
    do j = 0, r_s-1
      buf(n-j) = buf(n-j) * dble(j) / dble(r_s)
    end do
  end subroutine
end program synth_fortran
