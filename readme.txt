so the address is 0x3d...
you offset it with the address in the doc(second value)
it gets a lil wonk if you read too fast so dont do that
there is the int pin which you may be able to read
using the gpio library.

so basically when you inevitably get back here:
the int pin (gray wire) pulls low when the FIFO
is non-empty.  when empty it returns to hi-z.

if you do write_byte_data(0x3d,0x11,0b.......x)
that'll set the beep to different things.
dot means 0 x means 1 idk yeah confusing.

ok cool guy.
