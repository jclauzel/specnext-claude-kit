/* z80ntime.c - measure Z80N instruction T-states on a ZX Spectrum Next by counting raster lines.
 *
 * For each CPU speed (NextReg $07 = 0..3) every block of timing.asm is run LOOPS times with interrupts off and the
 * lines it takes are counted. T for a block = 4 x (lines(block) - lines(empty)) / (lines(nop) - lines(empty)):
 * relative to nop (4 T), so it depends neither on the clock nor on the line length. The loops double with each
 * speed step, so lines / lines(nop at 3.5 MHz) also gives each block's cycles at that speed's own clock, wait states
 * included (the file's last column). The table stays on screen until a key is pressed, the results are also written
 * to Z80NTIME.TXT (CSV) in the current folder, and the program then gives back the CPU speed it found and leaves
 * through a soft reset (NextZXOS's .nex loader has no way back to BASIC).
 */

#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>
#include <input.h>
#include <arch/zxn.h>
#include <arch/zxn/esxdos.h>
#include <sys/ioctl.h>

/* the terminal's ioctls (from z88dk's config_zxn.h) */
#ifndef IOCTL_OTERM_PAUSE
#define IOCTL_OTERM_PAUSE 0xc042
#endif
#ifndef IOCTL_OTERM_CLS
#define IOCTL_OTERM_CLS 0x0102
#endif

extern void *m_block;
extern uint16_t m_loops;
extern uint16_t m_flen;
extern uint16_t measure_run(void);
extern uint16_t frame_lines(void);
extern void set_speed(uint8_t s) __z88dk_fastcall;
extern uint8_t read_reg(uint8_t r) __z88dk_fastcall;
extern void soft_reset(void);

extern uint8_t blk_empty[], blk_nop[], blk_and[], blk_test[], blk_pushnn[], blk_pushhl[], blk_addhla[], blk_mul[],
               blk_addhlde[];

#define NTEST 9                 /* the empty block first, nop second */
#define NSPEED 4
#define LOOPS0 64              /* loops at 3.5 MHz; doubled at each speed step so the line counts stay alike */

static void *const block[NTEST] = {
    blk_empty, blk_nop, blk_and, blk_test, blk_pushnn, blk_pushhl, blk_addhla, blk_mul, blk_addhlde
};

/* screen labels: at most 11 characters */
static const char *const label[NTEST] = {
    "(loop)", "nop", "and n", "test n", "push nn/pop", "ld/push/pop", "add hl,a", "mul d,e", "ld/ld/add"
};

/* file labels: the instructions in full */
static const char *const full[NTEST] = {
    "empty block (call+ret+line read)", "nop", "and n", "test n", "push nn + pop hl", "ld hl,nn + push hl + pop hl",
    "add hl,a", "mul d,e", "ld e,a + ld d,0 + add hl,de"
};

static const char *const mhz[NSPEED] = { "3.5", "7", "14", "28" };

static uint16_t lines[NSPEED][NTEST];   /* raw lines, the empty block included */
static uint16_t tx10[NSPEED][NTEST];    /* T x 10 per block, rounded */
static uint16_t cx10[NSPEED][NTEST];    /* cycles x 10 of that speed's clock, against the 3.5 MHz nop */
static uint16_t flen;
static uint8_t core1, core2;
static char buf[96];

static void measure_all(void)
{
    uint8_t s, t;
    uint16_t net, ref, ref0 = 1;

    set_speed(3);
    flen = frame_lines();               /* at 28 MHz: the read loop is then far shorter than a line */
    m_flen = flen;
    for (s = 0; s != NSPEED; ++s) {
        set_speed(s);
        m_loops = LOOPS0 << s;
        for (t = 0; t != NTEST; ++t) {
            m_block = block[t];
            lines[s][t] = measure_run();
        }
        ref = lines[s][1] - lines[s][0];
        if (!ref) ref = 1;              /* never divide by 0, even on a broken count */
        if (!s) ref0 = ref;
        for (t = 1; t != NTEST; ++t) {
            net = lines[s][t] - lines[s][0];
            tx10[s][t] = (uint16_t)(((uint32_t)net * 40 + ref / 2) / ref);
            /* the loops double with the clock, so equal cycles give equal lines: scale by the 3.5 MHz nop */
            cx10[s][t] = (uint16_t)(((uint32_t)net * 40 + ref0 / 2) / ref0);
        }
    }
}

static void show(void)
{
    uint8_t s, t;

    ioctl(1, IOCTL_OTERM_CLS);          /* clear the window and home the cursor */
    printf("Z80N TIMING TEST  core %u.%02u.%02u\n", core1 >> 4, core1 & 15, core2);
    printf("T/instr, nop=4. frame %u lines\n", flen);
    printf("%-11s%5s%5s%5s%5s\n", "MHz:", mhz[0], mhz[1], mhz[2], mhz[3]);
    for (t = 1; t != NTEST; ++t) {
        printf("%-11s", label[t]);
        for (s = 0; s != NSPEED; ++s)
            printf("%3u.%u", tx10[s][t] / 10, tx10[s][t] % 10);
        printf("\n");
    }
    printf("lines net, loops %u..%u\n", LOOPS0, LOOPS0 << 3);
    printf("%-11s%5s%5s%5s%5s\n", "MHz:", mhz[0], mhz[1], mhz[2], mhz[3]);
    for (t = 0; t != NTEST; ++t) {
        printf("%-11s", label[t]);
        for (s = 0; s != NSPEED; ++s)
            printf("%5u", t ? lines[s][t] - lines[s][0] : lines[s][0]);
        printf("\n");
    }
}

/* Write Z80NTIME.TXT (CSV) in the current folder; return 0 or the esxDOS error code. */
static uint8_t save(void)
{
    uint8_t h, s, t, err = 0;

    h = esx_f_open("Z80NTIME.TXT", ESX_MODE_W | ESX_MODE_OPEN_CREAT_TRUNC);
    if (h == 0xFF)
        return errno ? errno : 0xFF;
    sprintf(buf, "\"z80ntime: Z80N T-states measured by raster lines, relative to nop = 4 T\"\r\n");
    if (esx_f_write(h, buf, strlen(buf)) != strlen(buf)) err = errno ? errno : 0xFE;
    sprintf(buf, "core,%u.%02u.%02u\r\nframe_lines,%u\r\nblock_repeats,500\r\n", core1 >> 4, core1 & 15, core2, flen);
    if (!err && esx_f_write(h, buf, strlen(buf)) != strlen(buf)) err = errno ? errno : 0xFE;
    sprintf(buf, "mhz,instruction,loops,lines_net,t_states,cycles_vs_3.5mhz_nop\r\n");
    if (!err && esx_f_write(h, buf, strlen(buf)) != strlen(buf)) err = errno ? errno : 0xFE;
    for (s = 0; s != NSPEED && !err; ++s) {
        for (t = 0; t != NTEST && !err; ++t) {
            if (t)
                sprintf(buf, "%s,\"%s\",%u,%u,%u.%u,%u.%u\r\n", mhz[s], full[t], LOOPS0 << s,
                        lines[s][t] - lines[s][0], tx10[s][t] / 10, tx10[s][t] % 10, cx10[s][t] / 10, cx10[s][t] % 10);
            else
                sprintf(buf, "%s,\"%s\",%u,%u,,\r\n", mhz[s], full[t], LOOPS0 << s, lines[s][0]);
            if (esx_f_write(h, buf, strlen(buf)) != strlen(buf)) err = errno ? errno : 0xFE;
        }
    }
    if (esx_f_close(h) && !err) err = errno ? errno : 0xFD;
    return err;
}

int main(void)
{
    uint8_t speed0, err;

    speed0 = read_reg(0x07) & 3;        /* the speed NextZXOS ran at: given back at the end */
    core1 = read_reg(0x01);
    core2 = read_reg(0x0E);

    zx_border(INK_WHITE);
    ioctl(1, IOCTL_OTERM_PAUSE, 0);     /* never wait for a key when the text scrolls */
    ioctl(1, IOCTL_OTERM_CLS);
    printf("Z80N TIMING TEST\n\nMeasuring at 3.5, 7, 14, 28 MHz\n(about 6 seconds)...\n");

    measure_all();
    set_speed(speed0);

    show();
    errno = 0;
    err = save();
    if (err)
        printf("SAVE ERROR %u (Z80NTIME.TXT)\n", err);
    else
        printf("SAVED Z80NTIME.TXT\n");
    printf("PRESS A KEY TO EXIT");

    in_wait_nokey();
    in_wait_key();
    in_wait_nokey();
    ioctl(1, IOCTL_OTERM_CLS);
    soft_reset();                       /* NextZXOS starts again (the file is closed, the speed given back) */
    return 0;
}
