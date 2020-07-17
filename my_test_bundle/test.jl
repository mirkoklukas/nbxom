#!/usr/bin/env julia

using ArgParse
include("./experiment.jl")

settings = ArgParseSettings()
@add_arg_table! settings begin
    "--t"
        help = "Job-id provided by job manager"
	"--r"
        help = "Job-id provided by job manager"
end

parsed_args = parse_args(ARGS, settings)
println("Parsed args:")
for (arg,val) in parsed_args
    println("  $arg  =>  $val")
end



t = parsed_args["t"]
t = parse(Int,t)
println(t)
println(Int(t))
rd = joinpath(parsed_args["r"],"$t")
println(rd)

xargs = get_param(sweep_params, t)
println(xargs)

mkdir(rd)
run_nb_experiment(xargs...; task_id=t, results_dir=rd)