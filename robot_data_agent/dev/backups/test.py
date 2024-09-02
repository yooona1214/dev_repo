#%%
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

data = [('Zellweger', 3), ('Mcconaughey', 2), ('Grant', 1), ('Gibson', 1), ('Ryder', 1), ('Crawford', 2), ('Monroe', 2), ('Reynolds', 1), ('Stallone', 1), ('Harris', 3), ('Malden', 1), ('Chaplin', 1), ('Jovovich', 1), ('Keitel', 3), ('Cruise', 1), ('Cronyn', 2), ('Wood', 2), ('Suvari', 1), ('Birch', 1), ('Posey', 1), ('Witherspoon', 1), ('Wayne', 1), ('Tandy', 2), ('Kilmer', 5), ('Dean', 2), ('Peck', 3), ('Bacall', 1), ('Hawke', 1), ('Hurt', 1), ('Dern', 1), ('Barrymore', 1), ('Nicholson', 1), ('Close', 1), ('Chase', 2), ('Degeneres', 3), ('Pitt', 1), ('Heston', 1), ('Goldberg', 1), ('Olivier', 2), ('Bening', 2), ('Nolte', 4), ('Day-Lewis', 1), ('Neeson', 2), ('Brody', 2), ('Bergman', 1), ('Guiness', 3), ('Depp', 2), ('Garland', 3), ('Voight', 1), ('Hackman', 2), ('Carrey', 1), ('Dee', 2), ('Hope', 1), ('Walken', 1), ('Lollobrigida', 1), ('Dukakis', 2), ('Dreyfuss', 1), ('Costner', 1), ('Marx', 1), ('Wahlberg', 2), ('Pfeiffer', 1), ('Berry', 3), ('Torn', 3), ('Bloom', 1), ('Damon', 1), ('Hunt', 1), ('Sinatra', 1), ('Mostel', 2), ('Bullock', 1), ('Phoenix', 1), ('Leigh', 1), ('Streep', 2), ('Johansson', 3), ('Silverstone', 2), ('Paltrow', 2), ('West', 2), ('Wray', 1), ('Basinger', 1), ('Tomei', 1), ('Hudson', 1), ('Mckellen', 2), ('Bailey', 2), ('Jolie', 1), ('Sobieski', 1), ('Dunst', 1), ('Bergen', 1), ('Hopper', 2), ('Jackman', 2), ('Allen', 3), ('Bale', 1), ('Temple', 4), ('Gable', 1), ('Presley', 1), ('Miranda', 1), ('Swank', 1), ('Cage', 2), ('Gooding', 2), ('Cruz', 1), ('Pinkett', 1), ('Mansfield', 1), ('Winslet', 2), ('Astaire', 1), ('Bridges', 1), ('Pesci', 1), ('Mcdormand', 1), ('Mcqueen', 2), ('Tracy', 2), ('Penn', 2), ('Crowe', 1), ('Hoffman', 3), ('Akroyd', 3), ('Fawcett', 2), ('Williams', 3), ('Willis', 3), ('Hopkins', 3), ('Dench', 2), ('Ball', 1), ('Bolger', 2), ('Wilson', 1), ('Davis', 3), ('Tautou', 1)]
df = pd.DataFrame(data, columns=['Last Name', 'Count'])
code = plt.figure(figsize=(10,6))
sns.barplot(x='Count', y='Last Name', data=df, palette='viridis', edgecolor='black', legend=False)
plt.xlabel('Count')
plt.ylabel('Last Name')
plt.title('Distribution of Actor Last Names')
plt.show()
# %%
