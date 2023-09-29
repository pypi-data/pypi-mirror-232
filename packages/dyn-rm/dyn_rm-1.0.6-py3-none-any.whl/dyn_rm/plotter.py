import matplotlib
import matplotlib.pyplot as plt
import csv
import argparse

argParser = argparse.ArgumentParser()
argParser.add_argument("--input", type=str, help="The path to the input file", required=True)
argParser.add_argument("--output", type=str, help="The path to the output file", required=False)

args = argParser.parse_args()

input_file=None
output_file="output.pdf"
if None == args.input:
    raise Exception("No input given")
else:
    input_file=args.input

if None != args.output:
    output_file = args.output


colors = ['yellow', 'blue', 'green']
iterations = dict()
color_dict = dict()
header = None

with open(input_file) as file_obj:

    reader_obj = csv.reader(file_obj)
      
    # Iterate over each row in the csv 
    # file using reader object

    count = 0
    for row in reader_obj:
        if count == 0:
            header = row
            header_read = True
        else:
            iterations[count] = dict()
            for index in range(1, len(header)):
                if len(row) > index and row[index] != "":
                    iterations[count][header[index]] = row[index]
                    if(row[index] not in color_dict):
                        color_dict[row[index]] = colors[len(color_dict)]
                else:
                    iterations[count][header[index]] = None
        count += 1

  
fig = plt.figure(figsize=(4,3), constrained_layout=True)
ax = fig.add_subplot(111)

for index in range(1, len(header)):
    if index % 2== 0:
        ax.add_patch(matplotlib.patches.Rectangle((0, index), 60, 1, color=(0.5, 0.5, 0.5, 0.2)))
    else:
        ax.add_patch(matplotlib.patches.Rectangle((0, index), 60, 1, color=(0.5, 0.5, 0.5, 0.4)))
for iter in range (1, count):

    rectangles = []
  
    for index in range(1, len(header)):
        if None == iterations[iter][header[index]]:
            continue
        rectangles.append(matplotlib.patches.Rectangle((iter, index),
                                             1, 1,
                                             color = color_dict[iterations[iter][header[index]]]))
    
    for rect in rectangles:
        ax.add_patch(rect)

    
#plt.xlim([0, iter + 1])
plt.xlim([0, 60])
plt.ylim([1, index + 1])

plt.yticks([x for x in range(1, len(header))], visible=False)
for i, label in enumerate(header[1:]):
    ax.text(-5, i + 1.5, label, ha='left', va='center')
labels = []
for x in range(1, 60):
    if x%10 == 0:
        labels.append(str(x))
    else:
        labels.append("") 
    
plt.xticks(ticks=[x for x in range (1, 60)], labels = labels)
plt.xlabel("Iteration of Scheduling Loop", fontweight='bold')
plt.ylabel("Nodes", labelpad=20, fontweight='bold')
plt.grid(which='major', axis='both')
for i, job in enumerate(color_dict.keys()):
    plt.bar(0, 0, width=0.8, color=color_dict[job], label="Job"+str(i))
plt.legend()
    
ax.grid(which='major', axis='both', zorder=1)

plt.savefig(output_file)  
plt.show()