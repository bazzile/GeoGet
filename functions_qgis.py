def get_feature_list(vlayer):
    features_list = []
    field_names = [field.name() for field in vlayer.pendingFields()]
    for feature in vlayer.getFeatures():
        feature_values = [feature[field_name] for field_name in field_names]
        features_list.append(feature_values)
    return features_list


def get_values_from_layer(vlayer, column_name):
    values_list = []
    for feature in vlayer.getFeatures():
        value = feature[column_name]
        values_list.append(value)
    return values_list
