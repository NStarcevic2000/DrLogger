from types import SimpleNamespace

def get_namespaces(input_dict: dict, last_child_type:type, include_parent=False) -> SimpleNamespace:
    def recursive_namespace(store, last_child_type:type, prefix="") -> SimpleNamespace:
        namespace = {}
        for key, value in store.items():
            full_key = f"{prefix}.{key}" if prefix and include_parent else key
            if isinstance(value, dict):
                value = recursive_namespace(value, last_child_type, prefix=full_key.replace(' ',''))
                setattr(value, "name", full_key)
                namespace[full_key.replace(' ','')] = value
            elif isinstance(value, last_child_type):
                namespace[full_key.replace(' ','')] = value
            else:
                raise ValueError(f"Unsupported type '{type(value)}' as it is not Child({last_child_type}) or <class 'dict'>.")
        return SimpleNamespace(**namespace)
    return recursive_namespace(input_dict, last_child_type=last_child_type)