import itertools
from collections import Counter
from collections import defaultdict
from collections import deque
from math import prod
from typing import Counter as Count
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import pydantic
import rich.console
import rich.layout
import rich.live
import rich.markup
import rich.progress
import rich.rule
import rich.tree
import sage.matrix.constructor
import semver
import yaml
from sage.rings.integer_ring import ZZ

import autoeft
import autoeft.base.basis as eft_basis
import autoeft.base.classifications as classes
import autoeft.base.model as ir_model
import autoeft.construction.permutation_symmetries as sym_const
import autoeft.construction.symmetrizers as sym_reprs
import autoeft.form
import autoeft.io.basis as io_basis
from autoeft import exceptions
from autoeft import utils
from autoeft.base import tensors
from autoeft.combinatorics import generators
from autoeft.construction import invariants

print = autoeft.print  # noqa: A001


def construct_permutation_matrix(
    model: ir_model.Model,
    op_type: classes.Type,
    lorentz_tableaux: List[tensors.LorentzTableau],
    sun_groups_tableaux: Dict[str, List[tensors.SUNTableau]],
    combination: Count[Tuple[sym_reprs.GroupSymmetrizer, ...]],
    symmetrizer_matrices: Dict[
        sym_reprs.GroupSymmetrizer,
        Tuple[sage.matrix.constructor.Matrix, sage.matrix.constructor.Matrix],
    ],
    inverse_gram_matrices: Dict[str, sage.matrix.constructor.Matrix],
    threads: Optional[int] = None,
) -> Tuple[sage.matrix.constructor.Matrix, sage.matrix.constructor.Matrix]:
    ranks = defaultdict(set)
    pivots = defaultdict(set)
    permutation_matrices = []
    reduced_permutation_matrices = []
    for symmetrizer, cgc in combination.items():
        decomposition_matrix = sage.matrix.constructor.matrix.identity(1)
        reduced_decomposition_matrix = sage.matrix.constructor.matrix.identity(1)
        for group_symmetrizer in symmetrizer:
            if group_symmetrizer in symmetrizer_matrices:
                (
                    symmetrizer_matrix,
                    reduced_matrix,
                ) = symmetrizer_matrices[group_symmetrizer]
            else:
                group_name = group_symmetrizer.group_name
                if group_name == model.symmetries.lorentz_group.name:
                    basis = lorentz_tableaux
                    symmetrizer_matrix = sym_reprs.construct_lorentz_matrix(
                        op_type,
                        group_symmetrizer,
                        basis,
                    )
                else:
                    basis = sun_groups_tableaux[group_name]
                    group = model.symmetries.sun_groups[group_name]
                    symmetrizer_matrix = sym_reprs.construct_sun_matrix(
                        op_type,
                        group_symmetrizer,
                        basis,
                        group,
                        inverse_gram_matrices,
                        threads,
                    )
                rank = symmetrizer_matrix.rank()
                pivot = symmetrizer_matrix.pivot_rows()
                reduced_matrix = (
                    symmetrizer_matrix[pivot, :]
                    if pivot
                    else sage.matrix.constructor.matrix()
                )
                symmetrizer_matrices[group_symmetrizer] = (
                    symmetrizer_matrix,
                    reduced_matrix,
                )
                ranks[group_name].add(rank)
                pivots[group_name].add(pivot)
            decomposition_matrix = decomposition_matrix.tensor_product(
                symmetrizer_matrix,
                subdivide=False,
            )
            reduced_decomposition_matrix = reduced_decomposition_matrix.tensor_product(
                reduced_matrix,
                subdivide=False,
            )
        permutation_matrices.append(cgc * decomposition_matrix)
        reduced_permutation_matrices.append(cgc * reduced_decomposition_matrix)
    assert all(len(ranks) == 1 for ranks in ranks.values())
    assert all(len(pivots) == 1 for pivots in pivots.values())
    permutation_matrix = sum(permutation_matrices)
    reduced_permutation_matrix = sum(reduced_permutation_matrices)
    if reduced_permutation_matrix:
        reduced_permutation_matrix *= reduced_permutation_matrix.denominator()
        reduced_permutation_matrix = reduced_permutation_matrix.change_ring(ZZ)
        reduced_permutation_matrix /= reduced_permutation_matrix.gcd()
    reduced_permutation_matrix = reduced_permutation_matrix.change_ring(ZZ)
    return permutation_matrix, reduced_permutation_matrix


def plain_main(
    model: ir_model.Model,
    dimension: int,
    hc_flag: bool,
    gr_flag: bool,
    basis_file: io_basis.BasisFile,
    select: Optional[list] = None,
    ignore: Optional[list] = None,
    overwrite: bool = False,
    threads: Optional[int] = None,
) -> Tuple[Counter, Counter, Counter, Counter]:
    ct_family, ct_type, ct_term, ct_operator = (
        Counter(),
        Counter(),
        Counter(),
        Counter(),
    )
    tct_family, tct_type, tct_term, tct_operator = (
        Counter(),
        Counter(),
        Counter(),
        Counter(),
    )
    operator_status = rich.progress.Progress(
        rich.progress.SpinnerColumn(spinner_name="simpleDotsScrolling"),
        rich.progress.TextColumn("{task.description}", style="bold"),
    )
    status_task = operator_status.add_task("")
    stats_progress = rich.progress.Progress(
        rich.progress.TextColumn(
            "#[repr.attrib_name]{task.description}[/repr.attrib_name]"
            "="
            "[repr.number]{task.total:,}[/repr.number]([repr.number]{task.completed:,})[/repr.number]",
        ),
    )
    families_task = stats_progress.add_task("families", total=0)
    types_task = stats_progress.add_task("types", total=0)
    terms_task = stats_progress.add_task("terms", total=0)
    operators_task = stats_progress.add_task("operators", total=0)
    progress_group = rich.console.Group(
        operator_status,
        stats_progress,
    )
    with rich.live.Live(
        progress_group,
        console=autoeft.console,
        transient=True,
    ) as live:
        for family in invariants.construct_families(dimension, hc_flag, gr_flag):
            hc_mod = 1 if hc_flag or family.is_real() else 2
            for op_type in invariants.construct_types(family, model):
                operator_status.update(status_task, description=str(op_type))
                live.refresh()
                op_stats = basis_file.get_operator_raw_numbers(op_type.full_path())
                if op_stats:
                    terms_per_type, operators_per_type = op_stats
                    if terms_per_type:
                        tct_family[family] = hc_mod
                        tct_type[op_type] = hc_mod
                        tct_term[op_type] = hc_mod * terms_per_type
                        tct_operator[op_type] = hc_mod * operators_per_type
                        stats_progress.update(
                            families_task,
                            total=sum(tct_family.values()),
                        )
                        stats_progress.update(types_task, total=sum(tct_type.values()))
                        stats_progress.update(terms_task, total=sum(tct_term.values()))
                        stats_progress.update(
                            operators_task,
                            total=sum(tct_operator.values()),
                        )
                    if not overwrite:
                        continue
                if select and not utils.type_matches(op_type, select):
                    continue
                if ignore and utils.type_matches(op_type, ignore):
                    continue
                try:
                    lorentz_tableaux = invariants.construct_lorentz_tableaux(family)
                    sun_groups_tableaux = {
                        group_name: invariants.construct_sun_tableaux(op_type, group)
                        for group_name, group in model.symmetries.sun_groups.items()
                    }
                except exceptions.NoContractionException:
                    continue  # no invariant contractions found
                terms_per_type = 0
                operators_per_type = 0
                permutations_info = []
                symmetrizer_matrices = {}  # cache symmetrizer matrices
                inverse_gram_matrices = {}  # cache inverse Gram matrices
                allowed_group_permutations = sym_const.construct_group_permutations(
                    op_type,
                    model.symmetries,
                )
                permutation_symmetries = sym_const.construct_permutation_symmetries(
                    op_type,
                    allowed_group_permutations,
                )
                for permutation_symmetry in permutation_symmetries:
                    factorized_symmetries = sym_const.construct_factorized_symmetries(
                        *permutation_symmetry,
                    )
                    for symmetry, combination in factorized_symmetries:
                        (
                            permutation_matrix,
                            reduced_permutation_matrix,
                        ) = construct_permutation_matrix(
                            model,
                            op_type,
                            lorentz_tableaux,
                            sun_groups_tableaux,
                            combination,
                            symmetrizer_matrices,
                            inverse_gram_matrices,
                            threads,
                        )
                        terms_per_symmetry = reduced_permutation_matrix.nrows()
                        operators_per_symmetry = terms_per_symmetry * prod(
                            permutation.dimension_SUN(
                                model.fields[field_name].generations,
                            )
                            for field_name, permutation in symmetry.items()
                        )
                        if terms_per_symmetry:
                            permutation_info = (
                                eft_basis.PermutationSymmetryInfo.construct(
                                    symmetry=symmetry,
                                    n_terms=terms_per_symmetry,
                                    n_operators=operators_per_symmetry,
                                    matrix=reduced_permutation_matrix,
                                )
                            )
                            permutations_info.append(permutation_info)
                            terms_per_type += terms_per_symmetry
                            operators_per_type += operators_per_symmetry
                if terms_per_type:
                    type_info = (
                        op_type.to_counter(),
                        "real" if op_type.is_real(model) else "complex",
                    )
                    generations_info = Counter(
                        {f.name: f.generations for f, _ in op_type},
                    )
                    invariants_info = {
                        model.symmetries.lorentz_group.name: list(
                            zip(lorentz_tableaux, itertools.repeat(1)),
                        ),
                    }
                    invariants_info.update(
                        {
                            sun_group: list(zip(sun_tableaux, itertools.repeat(1)))
                            for sun_group, sun_tableaux in sun_groups_tableaux.items()
                        },
                    )
                    operator_info = eft_basis.OperatorInfoPermutation.construct(
                        model=model,
                        type=type_info,
                        generations=generations_info,
                        n_terms=terms_per_type,
                        n_operators=operators_per_type,
                        invariants=invariants_info,
                        permutation_symmetries=permutations_info,
                    )
                    basis_file.add_operator_info(operator_info)
                    print(repr(op_type), dest="log")
                    ct_family[family] = hc_mod
                    ct_type[op_type] = hc_mod
                    ct_term[op_type] = hc_mod * terms_per_type
                    ct_operator[op_type] = hc_mod * operators_per_type
                    tct_family[family] = hc_mod
                    tct_type[op_type] = hc_mod
                    tct_term[op_type] = hc_mod * terms_per_type
                    tct_operator[op_type] = hc_mod * operators_per_type
                    stats_progress.update(
                        families_task,
                        total=sum(tct_family.values()),
                        completed=sum(ct_family.values()),
                    )
                    stats_progress.update(
                        types_task,
                        total=sum(tct_type.values()),
                        advance=ct_type[op_type],
                    )
                    stats_progress.update(
                        terms_task,
                        total=sum(tct_term.values()),
                        advance=ct_term[op_type],
                    )
                    stats_progress.update(
                        operators_task,
                        total=sum(tct_operator.values()),
                        advance=ct_operator[op_type],
                    )
        operator_status.update(status_task, visible=False)
    print(
        f"[b]#[/b]families=[repr.number]{sum(tct_family.values()):,}[/repr.number]"
        f"([repr.number]{sum(ct_family.values()):,}[/repr.number])",
    )
    print(
        f"[b]#[/b]types=[repr.number]{sum(tct_type.values()):,}[/repr.number]"
        f"([repr.number]{sum(ct_type.values()):,}[/repr.number])",
    )
    print(
        f"[b]#[/b]terms=[repr.number]{sum(tct_term.values()):,}[/repr.number]"
        f"([repr.number]{sum(ct_term.values()):,}[/repr.number])",
    )
    print(
        f"[b]#[/b]operators=[repr.number]{sum(tct_operator.values()):,}[/repr.number]"
        f"([repr.number]{sum(ct_operator.values()):,}[/repr.number])",
    )
    return tct_family, tct_type, tct_term, tct_operator


def verbose_main(  # noqa: C901
    model: ir_model.Model,
    dimension: int,
    hc_flag: bool,
    gr_flag: bool,
    basis_file: io_basis.BasisFile,
    select: Optional[list] = None,
    ignore: Optional[list] = None,
    overwrite: bool = False,
    threads: Optional[int] = None,
) -> Tuple[Counter, Counter, Counter, Counter]:
    ct_family, ct_type, ct_term, ct_operator = (
        Counter(),
        Counter(),
        Counter(),
        Counter(),
    )
    tct_family, tct_type, tct_term, tct_operator = (
        Counter(),
        Counter(),
        Counter(),
        Counter(),
    )
    eft_tree = rich.tree.Tree(
        f"[d]{rich.markup.escape(model.name)}[/d] @ [i]d={dimension}[/i]",
        style="bold",
        highlight=True,
    )
    render_eft_tree = rich.tree.Tree(
        f"[d]{rich.markup.escape(model.name)}[/d] @ [i]d={dimension}[/i]",
        style="bold",
        highlight=True,
    )
    render_eft_tree.children = deque(maxlen=1)
    operator_status = rich.progress.Progress(
        rich.progress.SpinnerColumn(spinner_name="simpleDotsScrolling"),
        rich.progress.TextColumn("{task.description}", style="bold"),
    )
    status_task = operator_status.add_task("")
    layout = rich.layout.Layout(name="root")
    layout.split_column(
        rich.layout.Layout(rich.rule.Rule(), name="header", size=1),
        rich.layout.Layout(render_eft_tree, name="tree"),
        rich.layout.Layout(rich.rule.Rule(), name="rule", size=1),
        rich.layout.Layout(operator_status, name="status", size=1),
    )
    tree_height = layout.render(autoeft.console, autoeft.console.options)[
        layout["tree"]
    ].region.height
    with rich.live.Live(layout, console=autoeft.console, transient=True) as live:
        for family in invariants.construct_families(dimension, hc_flag, gr_flag):
            layout["header"].update(rich.rule.Rule(family.tuple_repr()))
            hc_mod = 1 if hc_flag or family.is_real() else 2
            hc_str = (
                "" if hc_flag or family.is_real() else "[dim italic not bold] + h.c.[/]"
            )
            family_tree = eft_tree.add(
                str(family) + hc_str,
                style="bold",
                highlight=True,
            )
            render_family_tree = render_eft_tree.add(
                str(family) + hc_str,
                style="bold",
                highlight=True,
            )
            render_family_tree.children = deque(maxlen=(tree_height - 2) // 3)

            for op_type in invariants.construct_types(family, model):
                operator_status.update(status_task, description=str(op_type) + hc_str)
                live.refresh()
                op_stats = basis_file.get_operator_raw_numbers(op_type.full_path())
                if op_stats:
                    terms_per_type, operators_per_type = op_stats
                    if terms_per_type:
                        tct_family[family] = hc_mod
                        tct_type[op_type] = hc_mod
                        tct_term[op_type] = hc_mod * terms_per_type
                        tct_operator[op_type] = hc_mod * operators_per_type
                    if not overwrite:
                        if tct_term[op_type]:
                            type_tree = family_tree.add(str(op_type) + hc_str)
                            type_tree.add(
                                f"#terms={tct_term[op_type]}",
                                style="not bold dim",
                            )
                            type_tree.add(
                                f"#operators={tct_operator[op_type]}",
                                style="not bold dim",
                            )
                            render_type_tree = render_family_tree.add(
                                str(op_type) + hc_str,
                            )
                            render_type_tree.add(
                                f"#terms={tct_term[op_type]}",
                                style="not bold dim",
                            )
                            render_type_tree.add(
                                f"#operators={tct_operator[op_type]}",
                                style="not bold dim",
                            )
                        continue
                if select and not utils.type_matches(op_type, select):
                    if tct_term[op_type]:
                        type_tree = family_tree.add(str(op_type) + hc_str)
                        type_tree.add(
                            f"#terms={tct_term[op_type]}",
                            style="not bold dim",
                        )
                        type_tree.add(
                            f"#operators={tct_operator[op_type]}",
                            style="not bold dim",
                        )
                        render_type_tree = render_family_tree.add(str(op_type) + hc_str)
                        render_type_tree.add(
                            f"#terms={tct_term[op_type]}",
                            style="not bold dim",
                        )
                        render_type_tree.add(
                            f"#operators={tct_operator[op_type]}",
                            style="not bold dim",
                        )
                    continue
                if ignore and utils.type_matches(op_type, ignore):
                    if tct_term[op_type]:
                        type_tree = family_tree.add(str(op_type) + hc_str)
                        type_tree.add(
                            f"#terms={tct_term[op_type]}",
                            style="not bold dim",
                        )
                        type_tree.add(
                            f"#operators={tct_operator[op_type]}",
                            style="not bold dim",
                        )
                        render_type_tree = render_family_tree.add(str(op_type) + hc_str)
                        render_type_tree.add(
                            f"#terms={tct_term[op_type]}",
                            style="not bold dim",
                        )
                        render_type_tree.add(
                            f"#operators={tct_operator[op_type]}",
                            style="not bold dim",
                        )
                    continue
                try:
                    lorentz_tableaux = invariants.construct_lorentz_tableaux(family)
                    sun_groups_tableaux = {
                        group_name: invariants.construct_sun_tableaux(op_type, group)
                        for group_name, group in model.symmetries.sun_groups.items()
                    }
                except exceptions.NoContractionException:
                    continue  # no invariant contractions found
                terms_per_type = 0
                operators_per_type = 0
                permutations_info = []
                symmetrizer_matrices = {}  # cache symmetrizer matrices
                inverse_gram_matrices = {}  # cache inverse Gram matrices
                allowed_group_permutations = sym_const.construct_group_permutations(
                    op_type,
                    model.symmetries,
                )
                permutation_symmetries = sym_const.construct_permutation_symmetries(
                    op_type,
                    allowed_group_permutations,
                )
                for permutation_symmetry in permutation_symmetries:
                    factorized_symmetries = sym_const.construct_factorized_symmetries(
                        *permutation_symmetry,
                    )
                    for symmetry, combination in factorized_symmetries:
                        (
                            permutation_matrix,
                            reduced_permutation_matrix,
                        ) = construct_permutation_matrix(
                            model,
                            op_type,
                            lorentz_tableaux,
                            sun_groups_tableaux,
                            combination,
                            symmetrizer_matrices,
                            inverse_gram_matrices,
                            threads,
                        )
                        terms_per_symmetry = reduced_permutation_matrix.nrows()
                        operators_per_symmetry = terms_per_symmetry * prod(
                            permutation.dimension_SUN(
                                model.fields[field_name].generations,
                            )
                            for field_name, permutation in symmetry.items()
                        )
                        if terms_per_symmetry:
                            permutation_info = (
                                eft_basis.PermutationSymmetryInfo.construct(
                                    symmetry=symmetry,
                                    n_terms=terms_per_symmetry,
                                    n_operators=operators_per_symmetry,
                                    matrix=reduced_permutation_matrix,
                                )
                            )
                            permutations_info.append(permutation_info)
                            terms_per_type += terms_per_symmetry
                            operators_per_type += operators_per_symmetry
                if terms_per_type:
                    type_info = (
                        op_type.to_counter(),
                        "real" if op_type.is_real(model) else "complex",
                    )
                    generations_info = Counter(
                        {f.name: f.generations for f, _ in op_type},
                    )
                    invariants_info = {
                        model.symmetries.lorentz_group.name: list(
                            zip(lorentz_tableaux, itertools.repeat(1)),
                        ),
                    }
                    invariants_info.update(
                        {
                            sun_group: list(zip(sun_tableaux, itertools.repeat(1)))
                            for sun_group, sun_tableaux in sun_groups_tableaux.items()
                        },
                    )
                    operator_info = eft_basis.OperatorInfoPermutation.construct(
                        model=model,
                        type=type_info,
                        generations=generations_info,
                        n_terms=terms_per_type,
                        n_operators=operators_per_type,
                        invariants=invariants_info,
                        permutation_symmetries=permutations_info,
                    )
                    basis_file.add_operator_info(operator_info)
                    print(repr(op_type), dest="log")
                    ct_family[family] = hc_mod
                    ct_type[op_type] = hc_mod
                    ct_term[op_type] = hc_mod * terms_per_type
                    ct_operator[op_type] = hc_mod * operators_per_type
                    tct_family[family] = hc_mod
                    tct_type[op_type] = hc_mod
                    tct_term[op_type] = hc_mod * terms_per_type
                    tct_operator[op_type] = hc_mod * operators_per_type
                    type_tree = family_tree.add(str(op_type) + hc_str)
                    type_tree.add(f"#terms={ct_term[op_type]}", style="not bold")
                    type_tree.add(
                        f"#operators={ct_operator[op_type]}",
                        style="not bold",
                    )
                    render_type_tree = render_family_tree.add(str(op_type) + hc_str)
                    render_type_tree.add(f"#terms={ct_term[op_type]}", style="not bold")
                    render_type_tree.add(
                        f"#operators={ct_operator[op_type]}",
                        style="not bold",
                    )
        layout["header"].update(rich.rule.Rule())
    print(eft_tree)
    autoeft.console.rule()
    print(
        f"[b]#[/b]families=[repr.number]{sum(tct_family.values()):,}[/repr.number]"
        f"([repr.number]{sum(ct_family.values()):,}[/repr.number])",
    )
    print(
        f"[b]#[/b]types=[repr.number]{sum(tct_type.values()):,}[/repr.number]"
        f"([repr.number]{sum(ct_type.values()):,}[/repr.number])",
    )
    print(
        f"[b]#[/b]terms=[repr.number]{sum(tct_term.values()):,}[/repr.number]"
        f"([repr.number]{sum(ct_term.values()):,}[/repr.number])",
    )
    print(
        f"[b]#[/b]operators=[repr.number]{sum(tct_operator.values()):,}[/repr.number]"
        f"([repr.number]{sum(ct_operator.values()):,}[/repr.number])",
    )
    return tct_family, tct_type, tct_term, tct_operator


def dry_run(
    model: ir_model.Model,
    dimension: int,
    hc_flag: bool,
    gr_flag: bool,
    select: Optional[list] = None,
    ignore: Optional[list] = None,
):
    for family in invariants.construct_families(dimension, hc_flag, gr_flag):
        for op_type in invariants.construct_types(family, model):
            if select and not utils.type_matches(op_type, select):
                continue
            if ignore and utils.type_matches(op_type, ignore):
                continue
            yield op_type


def main(args) -> int:
    form_version_min = semver.Version(4, 3)
    if autoeft.form.version < form_version_min:
        errmsg = (
            f"The version of FORM installed is not compatible with {autoeft.program}."
            "\n"
            f"Please install FORM version {form_version_min} or higher."
        )
        raise exceptions.RequirementVersionError(errmsg)
    model_path = args.model.resolve()
    dimension = args.dimension
    output_path = args.output.resolve()
    output_path /= f"{model_path.stem}-eft"
    generators.default_path = args.generators.resolve()
    try:
        with model_path.open("r") as model_file:
            model = ir_model.Model(**yaml.safe_load(model_file))
    except (FileNotFoundError, IsADirectoryError):
        errmsg = f"Model file not found {model_path}."
        print(errmsg)
        return 1
    except pydantic.ValidationError as e:
        errmsg = f"{e}\nCould not validate model."
        print(errmsg)
        return 1
    except yaml.YAMLError as e:
        errmsg = f"{e}\nCould not parse model file."
        print(errmsg)
        return 1
    hc_flag = not args.no_hc
    gr_flag = any(abs(f.helicity) == 2 for f in model.fields.values())
    print(model)
    print()

    try:
        select = (
            [yaml.safe_load(s.replace(":", ": ")) for s in args.select]
            if args.select
            else None
        )
        ignore = (
            [yaml.safe_load(i.replace(":", ": ")) for i in args.ignore]
            if args.ignore
            else None
        )
    except yaml.YAMLError as e:
        errmsg = f"{e}\nCould not parse select/ignore options."
        print(errmsg)
        return 1
    if args.dry_run:
        print(
            f"Dry run for "
            f"[b]{rich.markup.escape(model.name)}[/b] @ [i]d={dimension}[/i]",
        )
        print(f"[i]select[/i]: {select}")
        print(f"[i]ignore[/i]: {ignore}")
        print()
        print("[b]types:[/b]")
        for op_type in dry_run(
            model,
            dimension,
            hc_flag,
            gr_flag,
            select,
            ignore,
        ):
            print(f"[bold white]{op_type}[/bold white]", dest="terminal")
            print(op_type, dest="log")
        return 0

    wd = output_path / ascii(dimension)
    wd.mkdir(parents=True, exist_ok=True)
    basis_path = wd / "basis"
    basis_file = io_basis.BasisFile(basis_path)
    if basis_file:
        existing_model = basis_file.get_model()
        if model != existing_model:
            errmsg = (
                "Incompatible model files."
                "\n"
                f"The basis directory {basis_path} already exists"
                " but it was created using a different model."
                "\n"
                "Please delete the existing basis directory"
                " or provide the same model as before."
            )
            print(errmsg)
            return 1
    else:
        basis_file.set_model(model)
    basis_file.set_extra(output_path.name, dimension, args)

    if args.threads <= 0:
        errmsg = f"Number of threads must be greater than 0, not '{args.threads}'."
        print(errmsg)
        return 1

    print(
        f"Constructing operator basis for "
        f"[b]{rich.markup.escape(model.name)}[/b] @ [i]d={dimension}[/i]",
    )
    main_func = verbose_main if not args.quiet and args.verbose else plain_main
    ct_family, ct_type, ct_term, ct_operator = main_func(
        model,
        dimension,
        hc_flag,
        gr_flag,
        basis_file,
        select,
        ignore,
        args.overwrite,
        args.threads,
    )
    stats = {}
    stats["n_families"] = int(sum(ct_family.values()))
    stats["n_types"] = int(sum(ct_type.values()))
    stats["n_terms"] = int(sum(ct_term.values()))
    stats["n_operators"] = int(sum(ct_operator.values()))
    stats_path = wd / "stats.yml"
    stats_path.write_text(yaml.safe_dump(stats, sort_keys=False))
    print(f"Saved operators in {basis_file.basis_path}")
    return 0
