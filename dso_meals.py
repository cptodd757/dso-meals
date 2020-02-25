import numpy as np 
import pandas as pd 

DEBUG = False
MAX_SIZE = 5

def debug(printable):
    if not DEBUG:
        return
    print(printable)

def first_word(string):
    return string[:string.index(" ")]

def data_clean(filename):
    df = pd.read_csv(filename)
    df = df.dropna(subset=['Name'],how='any')
    df = df.fillna("none")

    days_list = [col for col in df.columns if 'day' in col]
    #debug(days_list)
    def create_headers(row):
        for day in days_list:
            #debug(row)
            if row[day] == "none":
                continue
            times = row[day].split(', ')
            #debug(times)
            for time in times:
                new_header = first_word(day) + ' ' + time
                row[new_header] = 1
        return row

    df = df.apply(create_headers,axis=1)
    df = df.drop(days_list,axis=1)
    df = df.fillna(0)
    return df

TIME_OPTIONS = []
TIME_OPTION_COUNTS = []
def get_counts(df):
    def get_counts_by_col(col):
        if 'day' in col.name:
            TIME_OPTIONS.append(col.name)
            TIME_OPTION_COUNTS.append(int(np.sum(np.array(col))))
            return col
    df = df.apply(get_counts_by_col)

def sum_availability(df):
    non_numeric = [col for col in df.columns if 'day' not in col]
    def sum_per_row(row):
        row["total"] = np.sum(np.array(row.drop(non_numeric)))
        return row
    df = df.apply(sum_per_row,axis=1)
    return df

def assign_groups(df):
    ###final answer:
    group_times = []
    group_members = []
    group_sizes = []
    ###

    people_order = np.argsort(np.array(df["total"]))
    debug(np.array(df["total"]))
    debug(people_order)

    numeric = [col for col in df.columns if 'day' in col]
    debug(numeric)
    for person in people_order:
        options = [col for col in numeric if df.iloc[person][col]]

        groups_order = np.argsort(group_sizes)
        debug(groups_order)
        group_found = False
        for group in groups_order:
            if group_times[group] not in options:
                continue
            if group_sizes[group] < MAX_SIZE:
                group_sizes[group] += 1
                group_members[group].append(df.iloc[person]["Name"])
                group_found = True
                break
            else:
                break
        
        if not group_found:
            remaining_options = [option for option in options if option not in group_times]
            indices = [TIME_OPTIONS.index(option) for option in remaining_options]
            next_group = TIME_OPTIONS[indices[np.argmax([TIME_OPTION_COUNTS[index] for index in indices])]]
            group_times.append(next_group)
            group_sizes.append(1)
            group_members.append([df.iloc[person]["Name"]])
        
        debug([group_times,group_members,group_sizes])

    return [group_times,group_members,group_sizes]


fp = 'dso_meals_older.csv'
df = data_clean(fp)
df = sum_availability(df)
#df.to_csv('new_dso_meals.csv')
#debug(df)
get_counts(df)
answer = assign_groups(df)
debug(answer)