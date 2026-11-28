// geo.c - geometrogenesis toy: cool a complete graph under local rules.
//
// State: an undirected simple graph on N nodes, starting as the complete graph K_N
// (everything next to everything: no distance, no dimension).
//
// Energy (all terms local):
//   E = wa * sum_i (deg_i - D0)^2          valence: each node wants D0 links
//     + wb * sum_{edges e} (sq_e - S0)^2   flatness: each link wants to lie on S0 squares (4-cycles)
//     + wc * (#triangles)                  no triangles (a triangle is a tiny positively curved spot)
// The cubic lattice Z^3 has D0 = 6, S0 = 4 and no triangles, so it is a zero-energy state; so is
// Z^d with D0 = 2d, S0 = 2(d-1).
//
// Moves are local in the graph: remove a link; add a link to a node two steps away; slide a link's
// end to a neighbour of its far end. A small fraction of moves toggle a random pair (nonlocal).
// Metropolis acceptance with a geometric cooling schedule T0 -> T1.
//
// Bookkeeping: A (adjacency), C = A^2 (common-neighbour counts), S (squares through each edge),
// all updated incrementally. Squares through a new edge (i,j) are paths i-a-b-j.
//
// Time direction (optional, in the spirit of causal dynamical triangulations): with NT > 0 slices,
// node i lives at moment tau_i = i / (N/NT), time is periodic, and links may only join nodes in the
// same moment (space links) or in neighbouring moments (time links). The start is then the causal
// complete graph: every allowed link present. An optional worldline term
//   + wt * sum_i ((future_links_i - 1)^2 + (past_links_i - 1)^2)
// asks each point to have one link to the next moment and one to the previous one.
//
// With keep_whole = 1, space may not tear: a move that would split one moment's space into two
// pieces is refused (the graph version of CDT's fixed spatial topology).
//
// Usage: geo N D0 S0 wa wb wc T0 T1 moves seed outprefix nsnap [check] [init.edges|-] [NT] [wt] [keep_whole]
// Writes <outprefix>_<k>.edges snapshots and prints one stats line per snapshot.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>

static int N, D0, S0;
static double wa, wb, wc;
static uint8_t *A;
static int32_t *C, *S;
static int *nb, *deg, *pos;
static long long ntri;
static double E;
static int NT = 0, *tau, *fut, *pst;
static double wt = 0;
static inline double sqr(double x) { return x * x; }

// time relation of j seen from i: 0 same moment, +1 next moment, -1 previous moment, 9 not allowed
static inline int tdir(int i, int j) {
  if (NT == 0) return 0;
  int d = (tau[j] - tau[i] + NT) % NT;
  return d == 0 ? 0 : d == 1 ? 1 : d == NT - 1 ? -1 : 9;
}
static inline int allowed(int i, int j) { return tdir(i, j) != 9; }

// No tearing of space: with keep_whole set, a space link may only be removed if its two ends stay
// connected through the other space links of their moment (each moment's space stays one piece).
static int keep_whole = 0, *bfs_q, *seen_stamp, stamp = 0;
static int space_link_removable(int i, int j) {
  if (!keep_whole || tdir(i, j) != 0) return 1;
  stamp++;
  int head = 0, tail = 0;
  bfs_q[tail++] = i; seen_stamp[i] = stamp;
  while (head < tail) {
    int x = bfs_q[head++];
    for (int k = 0; k < deg[x]; k++) {
      int y = nb[(size_t)x * N + k];
      if (seen_stamp[y] == stamp || tau[y] != tau[i]) continue;
      if (x == i && y == j) continue;
      if (y == j) return 1;
      seen_stamp[y] = stamp; bfs_q[tail++] = y;
    }
  }
  return 0;
}
// change of the worldline energy when link (i,j) is added (sign=+1) or removed (sign=-1)
static double time_term(int i, int j, int sign) {
  int d = tdir(i, j);
  if (d == 0 || wt == 0) { if (d == 1) { fut[i] += sign; pst[j] += sign; } else if (d == -1) { pst[i] += sign; fut[j] += sign; } return 0; }
  int *a = d == 1 ? fut : pst, *b = d == 1 ? pst : fut;
  double dE = sqr(a[i] + sign - 1) - sqr(a[i] - 1) + sqr(b[j] + sign - 1) - sqr(b[j] - 1);
  a[i] += sign; b[j] += sign;
  return wt * dE;
}

static uint64_t rs;
static inline uint64_t rnd64(void) {
  uint64_t z = (rs += 0x9E3779B97F4A7C15ULL);
  z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
  z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
  return z ^ (z >> 31);
}
static inline double rndu(void) { return (rnd64() >> 11) * (1.0 / 9007199254740992.0); }
static inline int rndi(int n) { return (int)(rndu() * n); }

#define AD(i, j) A[(size_t)(i) * N + (j)]
#define CC(i, j) C[(size_t)(i) * N + (j)]
#define SS(i, j) S[(size_t)(i) * N + (j)]
#define NB(i, k) nb[(size_t)(i) * N + (k)]
#define POS(i, j) pos[(size_t)(i) * N + (j)]

static void list_add(int i, int j) { POS(i, j) = deg[i]; NB(i, deg[i]) = j; deg[i]++; }
static void list_del(int i, int j) {
  int p = POS(i, j), last = NB(i, deg[i] - 1);
  NB(i, p) = last; POS(i, last) = p; deg[i]--;
}

// structural add: update C, then A and lists (S handled separately)
static void add_struct(int i, int j) {
  for (int k = 0; k < deg[j]; k++) { int x = NB(j, k); CC(i, x)++; CC(x, i)++; }
  for (int k = 0; k < deg[i]; k++) { int x = NB(i, k); CC(j, x)++; CC(x, j)++; }
  CC(i, i)++; CC(j, j)++;
  AD(i, j) = AD(j, i) = 1;
  list_add(i, j); list_add(j, i);
}
static void del_struct(int i, int j) {
  AD(i, j) = AD(j, i) = 0;
  list_del(i, j); list_del(j, i);
  for (int k = 0; k < deg[j]; k++) { int x = NB(j, k); CC(i, x)--; CC(x, i)--; }
  for (int k = 0; k < deg[i]; k++) { int x = NB(i, k); CC(j, x)--; CC(x, j)--; }
  CC(i, i)--; CC(j, j)--;
}

// In a state WITHOUT edge (i,j): enumerate the squares i-a-b-j that the edge would close.
// Returns the change of the flatness energy on all OTHER edges when those squares appear
// (sigma=+1) or disappear (sigma=-1), applies it to S, and writes the square count to *sij.
static double sq_update(int i, int j, int sigma, int *sij) {
  double dE = 0; int s = 0;
  for (int k = 0; k < deg[i]; k++) {
    int a = NB(i, k), m = CC(a, j);
    if (!m) continue;
    s += m;
    int old = SS(i, a);
    dE += sqr(old + sigma * m - S0) - sqr(old - S0);
    SS(i, a) = SS(a, i) = old + sigma * m;
  }
  for (int k = 0; k < deg[j]; k++) {
    int b = NB(j, k), m = CC(i, b);
    if (!m) continue;
    int old = SS(j, b);
    dE += sqr(old + sigma * m - S0) - sqr(old - S0);
    SS(j, b) = SS(b, j) = old + sigma * m;
  }
  for (int k = 0; k < deg[i]; k++) {
    int a = NB(i, k);
    const uint8_t *Aa = A + (size_t)a * N;
    for (int l = 0; l < deg[j]; l++) {
      int b = NB(j, l);
      if (!Aa[b]) continue;
      int m = 1;
      if (AD(i, b) && AD(j, a)) { if (a > b) continue; m = 2; }
      int old = SS(a, b);
      dE += sqr(old + sigma * m - S0) - sqr(old - S0);
      SS(a, b) = SS(b, a) = old + sigma * m;
    }
  }
  *sij = s;
  return wb * dE;
}

static double do_add(int i, int j) {
  double dE = wa * (sqr(deg[i] + 1 - D0) - sqr(deg[i] - D0) + sqr(deg[j] + 1 - D0) - sqr(deg[j] - D0));
  int dtri = CC(i, j), s;
  dE += wc * dtri;
  dE += sq_update(i, j, +1, &s);
  SS(i, j) = SS(j, i) = s;
  dE += wb * sqr(s - S0);
  dE += time_term(i, j, +1);
  add_struct(i, j);
  ntri += dtri; E += dE;
  return dE;
}
static double do_remove(int i, int j) {
  int s_old = SS(i, j), s;
  del_struct(i, j);
  int dtri = CC(i, j);
  double dE = wa * (sqr(deg[i] - D0) - sqr(deg[i] + 1 - D0) + sqr(deg[j] - D0) - sqr(deg[j] + 1 - D0));
  dE -= wc * dtri;
  dE += sq_update(i, j, -1, &s);
  if (s != s_old) { fprintf(stderr, "square bookkeeping mismatch %d vs %d\n", s, s_old); exit(2); }
  dE -= wb * sqr(s_old - S0);
  dE += time_term(i, j, -1);
  ntri -= dtri; E += dE;
  return dE;
}

// full recomputation, for checking and drift control
static double recompute(long long *tri_out, int verify) {
  long long tri = 0; double e = 0; int bad = 0;
  for (int i = 0; i < N; i++) {
    e += wa * sqr(deg[i] - D0);
    for (int j = 0; j < N; j++) {
      int c = 0;
      for (int k = 0; k < deg[i]; k++) c += AD(NB(i, k), j);
      if (i != j && c != CC(i, j)) bad++;
      if (i == j && c != deg[i]) bad++;
    }
  }
  for (int i = 0; i < N; i++)
    for (int k = 0; k < deg[i]; k++) {
      int j = NB(i, k);
      if (j < i) continue;
      long long a3 = 0;
      for (int l = 0; l < deg[i]; l++) a3 += CC(NB(i, l), j);
      int s = (int)(a3 - (deg[i] + deg[j] - 1));
      if (s != SS(i, j)) bad++;
      e += wb * sqr(s - S0);
      tri += CC(i, j);
    }
  tri /= 3;
  e += wc * tri;
  if (NT) {
    for (int i = 0; i < N; i++) {
      int f = 0, p = 0;
      for (int k = 0; k < deg[i]; k++) {
        int d = tdir(i, NB(i, k));
        if (d == 1) f++; else if (d == -1) p++; else if (d == 9) bad++;
      }
      if (f != fut[i] || p != pst[i]) bad++;
      e += wt * (sqr(f - 1) + sqr(p - 1));
    }
  }
  if (verify && (bad || tri != ntri || fabs(e - E) > 1e-6 * (1 + fabs(e)))) {
    fprintf(stderr, "CHECK FAILED: bad=%d tri %lld vs %lld E %.6f vs %.6f\n", bad, tri, ntri, e, E);
    exit(3);
  }
  if (tri_out) *tri_out = tri;
  return e;
}

static void stats(long long step, double T, FILE *out, int k) {
  long long edges = 0, sqsum = 0, flat_edges = 0; int good_nodes = 0, iso = 0;
  for (int i = 0; i < N; i++) {
    if (deg[i] == 0) iso++;
    int good = deg[i] == D0;
    for (int q = 0; q < deg[i]; q++) {
      int j = NB(i, q);
      if (SS(i, j) != S0 || CC(i, j) != 0) good = 0;
      if (j > i) { edges++; sqsum += SS(i, j); if (SS(i, j) == S0 && CC(i, j) == 0) flat_edges++; }
    }
    if (good) good_nodes++;
  }
  long long tlinks = 0; int worldline = 0;
  if (NT) for (int i = 0; i < N; i++) { tlinks += fut[i]; if (fut[i] == 1 && pst[i] == 1) worldline++; }
  printf("snap %d step %lld T %.4g E %.1f edges %lld meandeg %.3f tri %lld meansq %.3f flat_edges %.3f lattice_nodes %.3f isolated %d time_links %lld worldline_nodes %.3f\n",
         k, step, T, E, edges, 2.0 * edges / N, ntri, edges ? (double)sqsum / edges : 0.0,
         edges ? (double)flat_edges / edges : 0.0, (double)good_nodes / N, iso, tlinks, (double)worldline / N);
  fflush(stdout);
  if (out) {
    for (int i = 0; i < N; i++)
      for (int q = 0; q < deg[i]; q++) { int j = NB(i, q); if (j > i) fprintf(out, "%d %d\n", i, j); }
  }
}

int main(int argc, char **argv) {
  if (argc < 13) {
    fprintf(stderr, "usage: geo N D0 S0 wa wb wc T0 T1 moves seed outprefix nsnap [check]\n");
    return 1;
  }
  N = atoi(argv[1]); D0 = atoi(argv[2]); S0 = atoi(argv[3]);
  wa = atof(argv[4]); wb = atof(argv[5]); wc = atof(argv[6]);
  double T0 = atof(argv[7]), T1 = atof(argv[8]);
  long long moves = atoll(argv[9]);
  rs = strtoull(argv[10], 0, 10) * 0x2545F4914F6CDD1DULL + 1;
  const char *prefix = argv[11];
  int nsnap = atoi(argv[12]);
  int check = argc > 13 ? atoi(argv[13]) : 0;

  A = calloc((size_t)N * N, 1);
  C = calloc((size_t)N * N, sizeof(int32_t));
  S = calloc((size_t)N * N, sizeof(int32_t));
  nb = calloc((size_t)N * N, sizeof(int));
  pos = calloc((size_t)N * N, sizeof(int));
  deg = calloc(N, sizeof(int));
  if (!A || !C || !S || !nb || !pos || !deg) { fprintf(stderr, "out of memory\n"); return 1; }

  const char *init = argc > 14 && strcmp(argv[14], "-") ? argv[14] : NULL;
  NT = argc > 15 ? atoi(argv[15]) : 0;
  wt = argc > 16 ? atof(argv[16]) : 0;
  keep_whole = argc > 17 ? atoi(argv[17]) : 0;
  bfs_q = calloc(N, sizeof(int)); seen_stamp = calloc(N, sizeof(int));
  if (NT && (NT < 3 || N % NT)) { fprintf(stderr, "need NT >= 3 dividing N\n"); return 1; }
  tau = calloc(N, sizeof(int)); fut = calloc(N, sizeof(int)); pst = calloc(N, sizeof(int));
  for (int i = 0; i < N; i++) tau[i] = NT ? i / (N / NT) : 0;

  if (init || NT) {
    if (init) {
      // continue from a saved snapshot (e.g. the network just after the complete graph collapsed)
      FILE *in = fopen(init, "r");
      if (!in) { fprintf(stderr, "cannot open %s\n", init); return 1; }
      int a, b;
      while (fscanf(in, "%d %d", &a, &b) == 2)
        if (a != b && !AD(a, b) && allowed(a, b)) { AD(a, b) = AD(b, a) = 1; list_add(a, b); list_add(b, a); }
      fclose(in);
    } else {
      // the causal complete graph: every link the time direction allows
      for (int i = 0; i < N; i++)
        for (int j = i + 1; j < N; j++)
          if (allowed(i, j)) { AD(i, j) = AD(j, i) = 1; list_add(i, j); list_add(j, i); }
    }
    for (int i = 0; i < N; i++)
      for (int k = 0; k < deg[i]; k++) { int d = tdir(i, NB(i, k)); if (d == 1) fut[i]++; else if (d == -1) pst[i]++; }
    for (int i = 0; i < N; i++)
      for (int j = 0; j < N; j++) { int c = 0; for (int k = 0; k < deg[i]; k++) c += AD(NB(i, k), j); CC(i, j) = c; }
    ntri = 0;
    for (int i = 0; i < N; i++)
      for (int k = 0; k < deg[i]; k++) {
        int j = NB(i, k);
        long long a3 = 0;
        for (int l = 0; l < deg[i]; l++) a3 += CC(NB(i, l), j);
        SS(i, j) = (int)(a3 - (deg[i] + deg[j] - 1));
        if (j > i) ntri += CC(i, j);
      }
    ntri /= 3;
  } else {
    // the complete graph, built exactly
    for (int i = 0; i < N; i++)
      for (int j = 0; j < N; j++) {
        if (i == j) { CC(i, i) = N - 1; continue; }
        AD(i, j) = 1; CC(i, j) = N - 2; SS(i, j) = (N - 2) * (N - 3);
        list_add(i, j);
      }
    ntri = (long long)N * (N - 1) * (N - 2) / 6;
  }
  E = 0; E = recompute(NULL, 0); recompute(NULL, 1);

  char fn[1024];
  snprintf(fn, sizeof fn, "%s_%03d.edges", prefix, 0);
  FILE *f = fopen(fn, "w"); stats(0, T0, f, 0); fclose(f);

  long long acc = 0, tries = 0;
  int snap = 1;
  long long next_snap = moves / nsnap;
  for (long long step = 1; step <= moves; step++) {
    double T = T0 * pow(T1 / T0, (double)step / moves);
    double r = rndu();
    int i = rndi(N);
    double dE;
    tries++;
    if (r < 0.01) {
      int j = rndi(N);
      if (j == i || !allowed(i, j)) continue;
      if (AD(i, j)) {
        if (!space_link_removable(i, j)) continue;
        dE = do_remove(i, j);
        if (dE > 0 && rndu() >= exp(-dE / T)) { do_add(i, j); } else acc++;
      } else {
        dE = do_add(i, j);
        if (dE > 0 && rndu() >= exp(-dE / T)) { do_remove(i, j); } else acc++;
      }
    } else if (r < 0.34) {                       // remove a link
      if (!deg[i]) continue;
      int j = NB(i, rndi(deg[i]));
      if (!space_link_removable(i, j)) continue;
      dE = do_remove(i, j);
      if (dE > 0 && rndu() >= exp(-dE / T)) do_add(i, j); else acc++;
    } else if (r < 0.67) {                       // add a link to a node two steps away
      if (!deg[i]) continue;
      int a = NB(i, rndi(deg[i]));
      int k = NB(a, rndi(deg[a]));
      if (k == i || AD(i, k) || !allowed(i, k)) continue;
      dE = do_add(i, k);
      if (dE > 0 && rndu() >= exp(-dE / T)) do_remove(i, k); else acc++;
    } else {                                     // slide a link's end one step
      if (!deg[i]) continue;
      int j = NB(i, rndi(deg[i]));
      int k = NB(j, rndi(deg[j]));
      if (k == i || AD(i, k) || !allowed(i, k) || !space_link_removable(i, j)) continue;
      dE = do_remove(i, j);
      dE += do_add(i, k);
      if (dE > 0 && rndu() >= exp(-dE / T)) { do_remove(i, k); do_add(i, j); } else acc++;
    }
    if (check && step % check == 0) recompute(NULL, 1);
    if (step >= next_snap && snap <= nsnap) {
      E = recompute(NULL, 0);
      snprintf(fn, sizeof fn, "%s_%03d.edges", prefix, snap);
      f = fopen(fn, "w"); stats(step, T, f, snap); fclose(f);
      snap++;
      next_snap = (long long)((double)moves * snap / nsnap);
    }
  }
  if (snap <= nsnap) {  // the last step may have been a skipped move; still write the final snapshot
    E = recompute(NULL, 0);
    snprintf(fn, sizeof fn, "%s_%03d.edges", prefix, snap);
    f = fopen(fn, "w"); stats(moves, T1, f, snap); fclose(f);
  }
  fprintf(stderr, "accepted %lld of %lld tries\n", acc, tries);
  return 0;
}
