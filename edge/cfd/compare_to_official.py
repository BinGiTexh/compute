#!/usr/bin/env python3
"""Compare AI pipeline detection events against Benny's official diver survey.

Usage:
    python compare_to_official.py --ai summary.csv --official peces_2023_2025.csv \
        --reef ESPERANZA --depth 20 --transect 1

The official CSV has one row per species encounter on a transect:
    Year, Month, Day, Region, Reef, Depth, Transect, Species

The AI CSV (v2) has one row per detection event:
    event_id, frame, fish_count, fish_count_raw, max_conf

Primary comparison metric: number of detection events (AI) vs number of
species encounters (Benny). Both represent "how many distinct fish were
seen along the transect" — the AI just can't tell species apart.
"""
import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def load_official(path, reef, depth, transect, year=2025):
    """Load Benny's CSV filtered to matching transect. Each row = 1 species encounter."""
    species_counts = Counter()
    total = 0
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Reef'].strip().strip('"').upper() != reef.upper():
                continue
            if int(row['Depth']) != depth:
                continue
            if row['Transect'].strip().strip('"') != str(transect):
                continue
            if int(row['Year']) != year:
                continue
            species = row['Species'].strip().strip('"')
            species_counts[species] += 1
            total += 1
    return species_counts, total


def load_ai(path):
    """Load AI pipeline summary CSV. Returns event count and per-event data."""
    events = []
    total_raw = 0
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        # v2 format: event_id, frame, fish_count, [fish_count_raw], max_conf
        if 'event_id' in fieldnames:
            for row in reader:
                raw = int(row.get('fish_count_raw', row['fish_count']))
                total_raw += raw
                events.append({
                    'frame': row['frame'],
                    'raw': raw,
                    'max_conf': float(row['max_conf']),
                })
        # v1 format: frame, fish_count_raw, fish_count_filtered, ...
        else:
            for row in reader:
                raw = int(row['fish_count_raw'])
                filtered = int(row['fish_count_filtered'])
                if filtered > 0:
                    total_raw += raw
                    events.append({
                        'frame': row['frame'],
                        'raw': raw,
                        'max_conf': float(row['max_conf']),
                    })
    n_events = len(events)
    return events, n_events, total_raw


def classify_by_size(species_counts):
    """Rough size classification of species for analysis."""
    small_species = {
        'Chromis limbaughi', 'Chromis atrilobata', 'Azurina atrilobata',
        'Stegastes rectifraenum', 'Stegastes flavilatus', 'Stegastes acapulcoensis',
        'Thalassoma lucasanum', 'Halichoeres dispilus', 'Halichoeres nicholsi',
        'Cirrhitichthys oxycephalus', 'Ophioblennius steindachneri',
        'Plagiotremus azaleus', 'Canthigaster punctatissima',
        'Serranus psittacinus', 'Johnrandallia nigrirostris',
        'Abudefduf troschelii',
    }
    medium_species = {
        'Prionurus punctatus', 'Prionurus laticlavius', 'Sufflamen verres',
        'Holacanthus passer', 'Bodianus diplotaenia', 'Mulloidichthys dentatus',
        'Scarus ghobban', 'Scarus compressus', 'Scarus rubroviolaceus',
        'Haemulon sexfasciatum', 'Haemulon maculicauda',
        'Arothron meleagris', 'Ostracion meleagris', 'Diodon holocanthus',
        'Myripristis leiognathus',
    }
    large_species = {
        'Lutjanus argentiventris', 'Lutjanus novemfasciatus', 'Lutjanus viridis',
        'Mycteroperca rosacea', 'Epinephelus labriformis',
        'Cephalopholis panamensis', 'Cephalopholis colonus',
        'Fistularia commersonii', 'Gymnothorax castaneus',
        'Seriola lalandi', 'Caranx caninus',
    }

    buckets = {'small (<15cm)': 0, 'medium (15-40cm)': 0, 'large (>40cm)': 0, 'unclassified': 0}
    for sp, count in species_counts.items():
        if sp in small_species:
            buckets['small (<15cm)'] += count
        elif sp in medium_species:
            buckets['medium (15-40cm)'] += count
        elif sp in large_species:
            buckets['large (>40cm)'] += count
        else:
            buckets['unclassified'] += count
    return buckets


def write_report(species_counts, ai_events, output_dir):
    """Write comparison_report.csv."""
    rows = []
    benny_total = sum(species_counts.values())

    for species, count in sorted(species_counts.items(), key=lambda x: -x[1]):
        rows.append({
            'category': species,
            'benny_encounters': count,
            'ai_events': '-',
            'difference': '-',
            'pct_difference': '-',
        })

    rows.append({
        'category': '--- TOTALS ---',
        'benny_encounters': benny_total,
        'ai_events': ai_events,
        'difference': ai_events - benny_total,
        'pct_difference': f"{((ai_events - benny_total) / benny_total * 100):.1f}%" if benny_total else 'N/A',
    })

    out_path = output_dir / 'comparison_report.csv'
    with open(out_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'category', 'benny_encounters', 'ai_events', 'difference', 'pct_difference'])
        writer.writeheader()
        writer.writerows(rows)
    return out_path


def make_chart(species_counts, ai_events, size_buckets, output_dir):
    """Bar chart: Benny species encounters vs AI detection events."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Left panel: encounter comparison
    ax = axes[0]
    benny_total = sum(species_counts.values())
    bars = ax.bar(
        ['Diver\n(species encounters)', 'AI\n(detection events)'],
        [benny_total, ai_events],
        color=['#2196F3', '#4CAF50'], edgecolor='black', linewidth=0.5)
    ax.set_ylabel('Number of encounters / events')
    ax.set_title('Fish Encounters: Diver Survey vs AI Pipeline')
    for bar, val in zip(bars, [benny_total, ai_events]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                str(val), ha='center', va='bottom', fontweight='bold')
    diff_pct = ((ai_events - benny_total) / benny_total * 100) if benny_total else 0
    ax.text(0.5, 0.92, f"AI is {diff_pct:+.1f}% vs diver",
            transform=ax.transAxes, ha='center', fontsize=10, style='italic')

    # Right panel: size bucket breakdown
    ax = axes[1]
    bucket_names = [k for k in size_buckets.keys() if size_buckets[k] > 0]
    bucket_vals = [size_buckets[k] for k in bucket_names]
    colors = {'small (<15cm)': '#FF9800', 'medium (15-40cm)': '#2196F3',
              'large (>40cm)': '#9C27B0', 'unclassified': '#9E9E9E'}
    bar_colors = [colors.get(k, '#9E9E9E') for k in bucket_names]
    bars = ax.bar(bucket_names, bucket_vals, color=bar_colors, edgecolor='black', linewidth=0.5)
    ax.set_ylabel('Count (diver)')
    ax.set_title("Diver Species by Size Class\n(AI detects all as generic 'fish')")
    for bar, val in zip(bars, bucket_vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                str(val), ha='center', va='bottom', fontsize=9)
    ax.tick_params(axis='x', rotation=15)

    plt.tight_layout()
    chart_path = output_dir / 'comparison_chart.png'
    plt.savefig(chart_path, dpi=150)
    plt.close()
    return chart_path


def print_summary(species_counts, ai_events, ai_raw, size_buckets, events, year):
    """Print readable terminal summary."""
    benny_total = sum(species_counts.values())
    diff = ai_events - benny_total
    pct = (diff / benny_total * 100) if benny_total else 0

    print("\n" + "=" * 70)
    print("  ESPERANZA TRANSECT — AI vs DIVER COMPARISON")
    print("=" * 70)

    print(f"\n  WHAT EACH NUMBER MEANS")
    print(f"  " + "-" * 66)
    print(f"  Benny (diver):  Each row in his CSV is one species encounter — a fish")
    print(f"                  he identified and recorded while swimming the transect.")
    print(f"                  His {year} survey logged {benny_total} encounters ({len(species_counts)} species).")
    print(f"  AI (pipeline):  Each detection event is a moment in the video where")
    print(f"                  the model saw fish that weren't in the previous frame.")
    print(f"                  The AI cannot identify species — it only knows 'fish'.")
    print(f"  " + "-" * 66)

    print(f"\n  {'METRIC':<40} {'DIVER':>10} {'AI':>10}")
    print(f"  " + "-" * 62)
    print(f"  {'Species encounters (diver) / events (AI)':<40} {benny_total:>10} {ai_events:>10}")
    print(f"  {'Raw fish detections (before dedup)':<40} {'—':>10} {ai_raw:>10}")
    print(f"  {'Difference':<40} {'':>10} {diff:>+10}")
    print(f"  {'Percent difference':<40} {'':>10} {pct:>+9.1f}%")

    print(f"\n  {'SIZE CLASS (diver breakdown)':<35} {'Count':>8} {'% of total':>12}")
    print(f"  " + "-" * 55)
    for bucket, count in sorted(size_buckets.items(), key=lambda x: -x[1]):
        if count > 0:
            pct_b = count / benny_total * 100 if benny_total else 0
            print(f"    {bucket:<33} {count:>8} {pct_b:>10.1f}%")

    print(f"\n  {'SPECIES LIST (diver, {})'.format(year):<35} {'Count':>8}")
    print(f"  " + "-" * 45)
    for species, count in sorted(species_counts.items(), key=lambda x: -x[1]):
        print(f"    {species:<33} {count:>8}")

    # Event-level stats
    if events:
        confs = [e['max_conf'] for e in events]
        print(f"\n  {'AI EVENT STATISTICS':<35}")
        print(f"  " + "-" * 45)
        print(f"    {'Total detection events':<33} {len(events):>8}")
        print(f"    {'Mean confidence':<33} {sum(confs)/len(confs):>8.3f}")
        print(f"    {'Min confidence':<33} {min(confs):>8.3f}")
        print(f"    {'Max confidence':<33} {max(confs):>8.3f}")
        high_conf = sum(1 for c in confs if c >= 0.50)
        print(f"    {'Events with conf >= 0.50':<33} {high_conf:>8}")

    print("\n" + "=" * 70)
    print("  INTERPRETATION")
    print("=" * 70)
    if diff > 0:
        print(f"\n  AI detects {diff} MORE events than the diver logged ({pct:+.1f}%)")
        print(f"  Likely causes:")
        print(f"    - Re-sighting: same fish appears in multiple non-consecutive frames")
        print(f"    - The diver swims a 25m line; the camera's field of view may")
        print(f"      capture fish off-transect that the diver would not count")
        print(f"    - Skip window (10s) may be too short for slow-moving fish")
    else:
        print(f"\n  AI detects {abs(diff)} FEWER events than the diver logged ({pct:+.1f}%)")
        print(f"  Likely causes:")
        print(f"    - Small/camouflaged fish below detection threshold")
        print(f"    - Fish in background missed at inference resolution")
        print(f"    - Brief appearances between sampled frames (1 per 5s)")

    print(f"\n  NOTE: The diver identifies species; the AI only detects presence.")
    print(f"  A perfect AI would match the diver's encounter count even without")
    print(f"  species ID — both are answering 'how many distinct fish did I see?'")

    print("\n" + "=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Compare AI detection events vs diver species encounters")
    parser.add_argument('--ai', required=True, help='AI pipeline summary.csv')
    parser.add_argument('--official', required=True, help="Benny's peces CSV")
    parser.add_argument('--reef', default='ESPERANZA', help='Reef name to filter')
    parser.add_argument('--depth', type=int, default=20, help='Depth in meters')
    parser.add_argument('--transect', default='1', help='Transect number')
    parser.add_argument('--year', type=int, default=2025, help='Survey year (default: 2025)')
    parser.add_argument('--output', default='.', help='Output directory')
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    species_counts, benny_total = load_official(
        args.official, args.reef, args.depth, args.transect, args.year)

    if benny_total == 0:
        print(f"ERROR: No records found for Reef={args.reef}, Depth={args.depth}, "
              f"Transect={args.transect}, Year={args.year}")
        print("Available combinations in file:")
        with open(args.official, newline='', encoding='utf-8-sig') as f:
            combos = set()
            for row in csv.DictReader(f):
                combos.add((row['Reef'].strip().strip('"'),
                            row['Depth'].strip(), row['Year'].strip()))
        for reef, depth, year in sorted(combos):
            print(f"  {reef} / {depth}m / {year}")
        sys.exit(1)

    events, ai_events, ai_raw = load_ai(args.ai)
    size_buckets = classify_by_size(species_counts)

    print_summary(species_counts, ai_events, ai_raw, size_buckets, events, args.year)

    report_path = write_report(species_counts, ai_events, output_dir)
    print(f"  Report saved: {report_path}")

    chart_path = make_chart(species_counts, ai_events, size_buckets, output_dir)
    print(f"  Chart saved:  {chart_path}\n")


if __name__ == '__main__':
    main()
