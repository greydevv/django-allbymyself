def get_path_name(model, page_name):
    opts = model._meta
    path_name = f'{opts.app_label}_{opts.model_name}_{page_name}'
    return path_name
