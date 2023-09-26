# Quality Data Extractor


QDE lets you extract the quality data from a generated data set. 

- Get a relatively smaller data set
- Generate new automated samples of it using any generative model.
- Pass both the sets into qde and get filtered combined data.

## How to use qde

Fit training, generated and test data into qde

```sh
qde_obj = qde.quality_data_extractor()
qde_obj.fit(train_set, new_set, test_set)
```

Get accuracy of unfiltered combined data

```sh
qde_obj.get_accuracy()
```

Get filtered data along with its accuracy using method 1

```sh
comb_data_1, accuracy_1 = qde_obj.get_combined_data(recipe=0)
```

Get filtered data along with its accuracy using method 2

```sh
comb_data_2, accuracy_2 = qde_obj.get_combined_data(recipe=1)
```