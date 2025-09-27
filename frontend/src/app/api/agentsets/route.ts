import { createClient, SupabaseClient } from "@supabase/supabase-js";
import { NextRequest, NextResponse } from "next/server"


const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

// Create client (if not passed in)
const supabase: SupabaseClient = createClient(supabaseUrl, supabaseAnonKey);
const { data, error } = await supabase.auth.signInWithPassword({
    email: process.env.NEXT_PUBLIC_SUPABASE_USER || "",
    password: "@@$h27hU706F%RCVD4mjo*^0b7@bl8^J"
})

if (error) {
    console.error('Supabase Login error:', error.message)
    // Handle error (show error message to user, etc.)
} else {
    console.log('SupabasedLogin successful:', data.user)
    // Handle success (redirect, update UI state, etc.)
}
export async function GET() {

    console.log(process.env.NEXT_PUBLIC_AGENTS_SET_TABLE_NAME)

    const { data, error } = await supabase
        .from(process.env.NEXT_PUBLIC_AGENTS_SET_TABLE_NAME as string)
        .select("*");

    console.log("fetched data: ", data)

    if (error) {
        throw new Error(`Failed to fetch agent set: ${error.message}`);
    }

    return NextResponse.json(data)
}
