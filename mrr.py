def calculate_mrr(file_path):
    # Open the file and read its lines
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Initialize variables for the loop
    i = 0
    sum = 0
    counter = 0

    # Iterate through the lines of the file
    while i < len(lines):
        # Check if the line contains 'Correct:'
        if 'Correct:' in lines[i]:
            # Extract the relevant part of the correct line
            correct_line = lines[i + 1].strip()
            parts = correct_line.split('/')
            correct_part = '/'.join(parts[3:]) # Skip the date part because sometimes it is wrong
            # print('Correct:', correct_part)

        # Check if the line contains 'Ranking:'
        if 'Ranking:' in lines[i]:
            i += 1
            ranking = 0
            # Iterate through the following lines until an empty line is encountered
            while i < len(lines) and lines[i].strip() != '':
                ranking_line = lines[i].strip()
                # Check if the correct part is present in the ranking line
                if correct_part in ranking_line:
                    ranking = int(ranking_line.split()[0])

                i += 1

            # Calculate MRR based on the ranking
            if ranking > 0:
                sum += 1 / ranking

            counter += 1
            # print('Ranking:', str(ranking))
            # print('\n')

        i += 1

    # Calculate and print the Mean Reciprocal Rank (MRR)
    mrr = sum / counter
    print('Number of instances:', str(counter))
    print('Reciprocal sum:', str(sum))
    print('MRR:', str(mrr))

# Example usage with 'results.txt' file
calculate_mrr('results.txt')
