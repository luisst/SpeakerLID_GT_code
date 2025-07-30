import pandas as pd


def load_data(file1, file2):
    cols = ['speaker_id', 'lang', 'start_time', 'end_time', 'filename']
    df1 = pd.read_csv(file1, sep='\t', header=None, names=cols)
    df2 = pd.read_csv(file2, sep='\t', header=None, names=cols)
    return df1, df2

def split_segments(row1, row2):
    results = []

    s1, e1 = row1['start_time'], row1['end_time']
    s2, e2 = row2['start_time'], row2['end_time']
    start_overlap = max(s1, s2)
    end_overlap = min(e1, e2)

    # Leading part of row1 (before overlap)
    if s1 < start_overlap:
        results.append({
            'speaker_id': row1['speaker_id'],
            'start_time': s1,
            'end_time': start_overlap
        })

    # Leading part of row2
    if s2 < start_overlap:
        results.append({
            'speaker_id': row2['speaker_id'],
            'start_time': s2,
            'end_time': start_overlap
        })

    # Overlapping part
    results.append({
        'speaker_id': f"{row1['speaker_id']}+{row2['speaker_id']}",
        'start_time': start_overlap,
        'end_time': end_overlap
    })

    # Trailing part of row1
    if e1 > end_overlap:
        results.append({
            'speaker_id': row1['speaker_id'],
            'start_time': end_overlap,
            'end_time': e1
        })

    # Trailing part of row2
    if e2 > end_overlap:
        results.append({
            'speaker_id': row2['speaker_id'],
            'start_time': end_overlap,
            'end_time': e2
        })

    return results

def find_overlaps(df1, df2):
    result_segments = []

    # Ensure times are numeric
    for df in [df1, df2]:
        df['start_time'] = pd.to_numeric(df['start_time'])
        df['end_time'] = pd.to_numeric(df['end_time'])

    used_1 = [False] * len(df1)
    used_2 = [False] * len(df2)

    for i, row1 in df1.iterrows():
        for j, row2 in df2.iterrows():
            s1, e1 = row1['start_time'], row1['end_time']
            s2, e2 = row2['start_time'], row2['end_time']

            # Check overlap
            if s1 < e2 and s2 < e1:
                segments = split_segments(row1, row2)
                result_segments.extend(segments)
                used_1[i] = True
                used_2[j] = True

    # Add untouched segments
    for i, row in df1.iterrows():
        if not used_1[i]:
            result_segments.append({
                'speaker_id': row['speaker_id'],
                'start_time': row['start_time'],
                'end_time': row['end_time']
            })

    for j, row in df2.iterrows():
        if not used_2[j]:
            result_segments.append({
                'speaker_id': row['speaker_id'],
                'start_time': row['start_time'],
                'end_time': row['end_time']
            })

    return pd.DataFrame(result_segments)


def main(file1, file2, output_file):
    df1, df2 = load_data(file1, file2)
    merged_df = find_overlaps(df1, df2)
    merged_df = merged_df.sort_values(by='start_time')
    merged_df.to_csv(output_file, sep='\t', index=False)

if __name__ == '__main__':
    file1 = r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\Proposal_runs\TTS3_dt\GT_final\D1_0.csv" 
    file2 = r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\Proposal_runs\TTS3_dt\GT_final\D2_0.csv" 
    output_file = r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\Proposal_runs\TTS3_dt\GT_final\DT_merged_gt.csv"
    main(file1, file2, output_file)
