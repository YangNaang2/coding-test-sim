// C++ 하네스 공통 헤더: 최소 JSON 파서, 매개변수 변환, 반환값 직렬화.
// 채점기가 문제의 시그니처에 맞춰 main.cpp를 생성하고 이 헤더와 사용자 코드를 포함한다.
#include <bits/stdc++.h>
using namespace std;

namespace ctj {

struct J {
    int t = 0;  // 0 null, 1 int, 2 double, 3 bool, 4 string, 5 array, 6 object
    long long i = 0;
    double d = 0;
    bool b = false;
    string s;
    vector<J> a;
    vector<pair<string, J>> o;
};

struct Parser {
    const string& x;
    size_t p = 0;
    explicit Parser(const string& s) : x(s) {}
    void ws() { while (p < x.size() && isspace((unsigned char)x[p])) p++; }
    static void utf8(string& out, unsigned cp) {
        if (cp < 0x80) out += (char)cp;
        else if (cp < 0x800) { out += (char)(0xC0 | (cp >> 6)); out += (char)(0x80 | (cp & 0x3F)); }
        else { out += (char)(0xE0 | (cp >> 12)); out += (char)(0x80 | ((cp >> 6) & 0x3F)); out += (char)(0x80 | (cp & 0x3F)); }
    }
    string str() {
        string r;
        p++;
        while (true) {
            char c = x[p++];
            if (c == '"') return r;
            if (c == '\\') {
                char e = x[p++];
                if (e == 'n') r += '\n';
                else if (e == 't') r += '\t';
                else if (e == 'r') r += '\r';
                else if (e == 'b') r += '\b';
                else if (e == 'f') r += '\f';
                else if (e == 'u') { utf8(r, (unsigned)stoul(x.substr(p, 4), nullptr, 16)); p += 4; }
                else r += e;
            } else r += c;
        }
    }
    J value() {
        ws();
        J v;
        char c = x[p];
        if (c == '{') {
            v.t = 6; p++; ws();
            if (x[p] == '}') { p++; return v; }
            while (true) {
                ws(); string k = str(); ws(); p++;
                v.o.push_back({k, value()});
                ws();
                if (x[p++] == '}') return v;
            }
        }
        if (c == '[') {
            v.t = 5; p++; ws();
            if (x[p] == ']') { p++; return v; }
            while (true) {
                v.a.push_back(value());
                ws();
                if (x[p++] == ']') return v;
            }
        }
        if (c == '"') { v.t = 4; v.s = str(); return v; }
        if (x.compare(p, 4, "true") == 0) { p += 4; v.t = 3; v.b = true; return v; }
        if (x.compare(p, 5, "false") == 0) { p += 5; v.t = 3; return v; }
        if (x.compare(p, 4, "null") == 0) { p += 4; return v; }
        size_t st = p;
        bool frac = false;
        while (p < x.size() && strchr("+-0123456789.eE", x[p])) {
            if (x[p] == '.' || x[p] == 'e' || x[p] == 'E') frac = true;
            p++;
        }
        string num = x.substr(st, p - st);
        if (frac) { v.t = 2; v.d = stod(num); } else { v.t = 1; v.i = stoll(num); v.d = (double)v.i; }
        return v;
    }
};

inline const J& get(const J& obj, const string& key) {
    for (auto& kv : obj.o) if (kv.first == key) return kv.second;
    throw runtime_error("missing key " + key);
}

template <class T> struct C;
template <> struct C<int> { static int f(const J& j) { return j.t == 2 ? (int)j.d : (int)j.i; } };
template <> struct C<long long> { static long long f(const J& j) { return j.t == 2 ? (long long)j.d : j.i; } };
template <> struct C<long> { static long f(const J& j) { return j.t == 2 ? (long)j.d : (long)j.i; } };
template <> struct C<double> { static double f(const J& j) { return j.t == 2 ? j.d : (double)j.i; } };
template <> struct C<bool> { static bool f(const J& j) { return j.b; } };
template <> struct C<string> { static string f(const J& j) { return j.s; } };
template <class T> struct C<vector<T>> {
    static vector<T> f(const J& j) {
        vector<T> v;
        v.reserve(j.a.size());
        for (auto& e : j.a) v.push_back(C<T>::f(e));
        return v;
    }
};

inline void esc(string& o, const string& s) {
    o += '"';
    for (unsigned char c : s) {
        if (c == '"') o += "\\\"";
        else if (c == '\\') o += "\\\\";
        else if (c == '\n') o += "\\n";
        else if (c == '\r') o += "\\r";
        else if (c == '\t') o += "\\t";
        else if (c < 0x20) { char buf[8]; snprintf(buf, sizeof buf, "\\u%04x", c); o += buf; }
        else o += (char)c;
    }
    o += '"';
}

inline void out(string& o, int v) { o += to_string(v); }
inline void out(string& o, long v) { o += to_string(v); }
inline void out(string& o, long long v) { o += to_string(v); }
inline void out(string& o, unsigned v) { o += to_string(v); }
inline void out(string& o, unsigned long v) { o += to_string(v); }
inline void out(string& o, unsigned long long v) { o += to_string(v); }
inline void out(string& o, bool v) { o += v ? "true" : "false"; }
inline void out(string& o, char v) { esc(o, string(1, v)); }
inline void out(string& o, double v) {
    if (!isfinite(v)) { o += "null"; return; }
    char buf[64];
    snprintf(buf, sizeof buf, "%.17g", v);
    o += buf;
}
inline void out(string& o, const string& v) { esc(o, v); }
inline void out(string& o, const char* v) { esc(o, string(v)); }
template <class T> void out(string& o, const vector<T>& v) {
    o += '[';
    for (size_t k = 0; k < v.size(); k++) {
        if (k) o += ',';
        out(o, (T)v[k]);
    }
    o += ']';
}

inline string readfile(const char* path) {
    ifstream f(path, ios::binary);
    stringstream ss;
    ss << f.rdbuf();
    return ss.str();
}

inline void send(const string& s) {
    string line = "@@CT@@" + s + "\n";
    fwrite(line.data(), 1, line.size(), stdout);
    fflush(stdout);
}

inline string captured(const ostringstream& cap) {
    string s = cap.str();
    if (s.size() > 20000) s = s.substr(0, 20000) + "\n...(출력이 너무 길어 생략)";
    string o;
    esc(o, s);
    return o;
}

}  // namespace ctj
